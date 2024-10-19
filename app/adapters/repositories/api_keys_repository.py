import abc
from collections.abc import Callable
from typing import AsyncContextManager

from app.adapters.orm.credentials.abusive_experience_keys import AbusiveExperienceKeyModel
from app.adapters.orm.credentials.virus_total_keys import VirusTotalKeyModel
from sqlalchemy import (
    func,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractAPIKeyRepository(abc.ABC):
    def __init__(self, session_factory: Callable[..., AsyncContextManager[AsyncSession]]):
        self.session_factory = session_factory

    @abc.abstractmethod
    async def load_keys_from_db(self) -> dict[str, int]:
        """Загрузить ключи API из базы данных."""
        raise NotImplementedError

    @abc.abstractmethod
    async def update_key_usage(self, api_key: str) -> None:
        """Обновить использование ключа API."""
        raise NotImplementedError

    @abc.abstractmethod
    async def reset_daily_limits(self) -> None:
        """Сбросить дневные лимиты использования ключей API."""
        raise NotImplementedError

    @abc.abstractmethod
    async def mark_as_invalid(self, api_key: str) -> None:
        """Отметить ключ API как недействительный."""
        raise NotImplementedError


class APIKeyRepository(AbstractAPIKeyRepository):
    def __init__(
        self,
        session_factory: Callable[..., AsyncContextManager[AsyncSession]],
        model: AbusiveExperienceKeyModel | VirusTotalKeyModel,
    ) -> None:
        super().__init__(session_factory)
        self.__model = model

    async def load_keys_from_db(self) -> dict[str, int]:
        keys_with_limits = {}
        async with self.session_factory() as session:
            result = await session.execute(
                select(
                    self.__model.api_key,
                    self.__model.daily_limit,
                    self.__model.used_limit,
                ).where(self.__model.is_valid == True),  # noqa
            )
            for api_key, daily_limit, used_limit in result:
                keys_with_limits[api_key] = daily_limit - used_limit

            return keys_with_limits

    async def update_key_usage(self, api_key: str) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(self.__model)
                .where(self.__model.api_key == api_key)  # noqa
                .values(used_limit=func.coalesce(self.__model.used_limit, 0) + 1),
            )
            await session.commit()

    async def reset_daily_limits(self) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(self.__model)
                .where(self.__model.is_valid == True)  # noqa
                .values(used_limit=0),
            )
            await session.commit()

    async def mark_as_invalid(self, api_key: str) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(self.__model)
                .where(self.__model.api_key == api_key)  # noqa
                .values(is_valid=False),
            )
            await session.commit()
