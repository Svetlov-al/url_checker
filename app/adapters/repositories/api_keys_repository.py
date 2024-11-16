import abc
from collections.abc import (
    Callable,
    Sequence,
)
from typing import AsyncContextManager

from app.adapters.orm.credentials.api_keys import (
    APIKeyModel,
    APIKeySourceType,
)
from app.core.constance import VT_DELAY
from app.domain.entities.api_key_entity import APIKeyEntity
from sqlalchemy import (
    func,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class AbstractAPIKeyRepository(abc.ABC):
    def __init__(self, session_factory: Callable[..., AsyncContextManager[AsyncSession]]):
        self.session_factory = session_factory

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


class APIKeyRepository(AbstractAPIKeyRepository):
    def __init__(
            self,
            session_factory: Callable[..., AsyncContextManager[AsyncSession]],
    ) -> None:
        super().__init__(session_factory)
        self.__model = APIKeyModel

    async def load_keys_from_db(self, keys_type: APIKeySourceType) -> list[APIKeyEntity]:
        async with self.session_factory() as session:
            query = (
                select(
                    self.__model,
                )
                .filter_by(
                    source=keys_type,
                    is_valid=True,
                )
                .filter(self.__model.used_limit < self.__model.daily_limit)
                .options(joinedload(self.__model.proxies))
            )

            res = await session.execute(query)
            res_orm = res.unique().scalars().all()

        return self._from_orm(rows=res_orm, keys_type=keys_type)

    async def update_key_usage(self, key_id: int) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(self.__model)
                .filter_by(id=key_id)
                .values(used_limit=func.coalesce(self.__model.used_limit, 0) + 1),
            )
            await session.commit()

    async def reset_daily_limits(self) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(self.__model)
                .filter_by(is_valid=True)
                .values(used_limit=0),
            )
            await session.commit()

    async def mark_as_invalid(self, key_id: int) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(self.__model)
                .filter_by(id=key_id)
                .values(is_valid=False),
            )
            await session.commit()

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
