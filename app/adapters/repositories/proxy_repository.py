import abc
import logging
from collections.abc import Callable
from typing import AsyncContextManager

from app.adapters.orm.proxy import ProxyModel
from app.domain.entities.proxy_entity import ProxyEntity
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractProxyRepository(abc.ABC):
    def __init__(self, session_factory: Callable[..., AsyncContextManager[AsyncSession]]):
        self.session_factory = session_factory

    @abc.abstractmethod
    async def get(self) -> ProxyEntity | None:
        raise NotImplementedError


logger = logging.getLogger(__name__)


class ProxyRepository(AbstractProxyRepository):
    def __init__(self, session_factory: Callable[..., AsyncContextManager[AsyncSession]]) -> None:
        super().__init__(session_factory)
        self.__model = ProxyModel

    async def get(self) -> ProxyEntity | None:
        async with self.session_factory() as session:
            result = (
                (
                    await session.execute(
                        select(self.__model)
                        .filter_by(
                            is_active=True,
                        ),
                    )
                )
                .scalars()
                .one_or_none()
            )
            if not result:
                return None

            return self._from_orm(result)

    @staticmethod
    def _from_orm(proxy: ProxyModel) -> ProxyEntity:
        """Преобразует ORM модель в доменную сущность."""
        return ProxyEntity(
            id=proxy.id,
            url=proxy.url,
            is_active=proxy.is_active,
        )
