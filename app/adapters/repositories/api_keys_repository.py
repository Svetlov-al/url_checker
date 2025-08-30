import abc
from collections.abc import Sequence

from app.adapters.orm.credentials.api_keys import (
    APIKeyModel,
    APIKeySourceType,
)
from app.core.constance import VT_DELAY
from app.database.mixins import QueryMixin
from app.domain.entities.api_key_entity import APIKeyEntity
from sqlalchemy import (
    func,
    select,
    update,
)
from sqlalchemy.orm import joinedload


class AbstractAPIKeyRepository(abc.ABC):
    @abc.abstractmethod
    async def load_keys_from_db(self, keys_type: APIKeySourceType) -> list[APIKeyEntity]:
        """Загрузить ключи API из базы данных."""
        raise NotImplementedError

    @abc.abstractmethod
    async def update_key_usage(self, key_id: int) -> None:
        """Обновить использование ключа API."""
        raise NotImplementedError

    @abc.abstractmethod
    async def reset_daily_limits(self) -> None:
        """Сбросить дневные лимиты использования ключей API."""
        raise NotImplementedError

    @abc.abstractmethod
    async def mark_as_invalid(self, key_id: int) -> None:
        """Отметить ключ API как недействительный."""
        raise NotImplementedError


class APIKeyRepository(AbstractAPIKeyRepository, QueryMixin):
    async def load_keys_from_db(self, keys_type: APIKeySourceType) -> list[APIKeyEntity]:
        query = (
            select(
                APIKeyModel,
            )
            .filter_by(
                source=keys_type,
                is_valid=True,
            )
            .filter(APIKeyModel.used_limit < APIKeyModel.daily_limit)
            .options(joinedload(APIKeyModel.proxies))
        )

        res = await self.session.execute(query)
        res_orm = res.unique().scalars().all()

        return self._from_orm(rows=res_orm, keys_type=keys_type)

    async def update_key_usage(self, key_id: int) -> None:
        await self.session.execute(
            update(APIKeyModel)
            .filter_by(id=key_id)
            .values(used_limit=func.coalesce(APIKeyModel.used_limit, 0) + 1),
        )
        await self.session.commit()

    async def reset_daily_limits(self) -> None:
        await self.session.execute(
            update(APIKeyModel)
            .filter_by(is_valid=True)
            .values(used_limit=0),
        )
        await self.session.commit()

    async def mark_as_invalid(self, key_id: int) -> None:
        await self.session.execute(
            update(APIKeyModel)
            .filter_by(id=key_id)
            .values(is_valid=False),
        )
        await self.session.commit()

    @staticmethod
    def _from_orm(
        rows: Sequence[APIKeyModel],
        keys_type: APIKeySourceType,
    ) -> list[APIKeyEntity]:
        keys_with_limits = []

        for row in rows:
            entity = APIKeyEntity(
                key_id=row.id,
                api_key=row.api_key,
                daily_limit=row.daily_limit,
                used_limit=row.used_limit,
                delay=VT_DELAY if keys_type.VIRUS_TOTAL else 0,
            )
            entity.add_proxies(row.proxies)
            keys_with_limits.append(entity)

        return keys_with_limits
