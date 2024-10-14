import abc
from collections.abc import Callable
from typing import AsyncContextManager

from adapters.orm import LinkModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.link_entity import LinkEntity


class AbstractRepository(abc.ABC):
    __model = None

    @abc.abstractmethod
    async def add(self, link: LinkEntity) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, url: str) -> LinkEntity | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_list(self, limit: int, offset: int, virus_total: bool) -> list[LinkEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def create_many(self, links: list[LinkEntity]) -> list[LinkEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_existing_links(self, urls: list[str]) -> list[str]:
        raise NotImplementedError


class LinkRepository(AbstractRepository):
    __model = LinkModel

    def __init__(self, session_factory: Callable[..., AsyncContextManager[AsyncSession]]) -> None:
        self.session_factory = session_factory

    async def add(self, link: LinkEntity) -> None:
        async with self.session_factory() as session:
            session.add(link.to_domain())
            await session.commit()

    async def get(self, url: str) -> LinkEntity | None:
        async with self.session_factory() as session:
            link_model = (
                (
                    await session.execute(
                        select(self.__model)
                        .filter_by(
                            url=url,
                        ),
                    )
                )
                .scalars()
                .one_or_none()
            )
            if not link_model:
                return None

            return self._from_orm(link_model)

    async def get_list(self, limit: int, offset: int, virus_total: bool) -> list[LinkEntity]:
        async with self.session_factory() as session:
            link_models = (
                (
                    await session.execute(
                        select(self.__model)
                        .filter_by(virus_total=virus_total)
                        .limit(limit)
                        .offset(offset),
                    )
                )
                .scalars()
                .all()
            )
            return [self._from_orm(link_model) for link_model in link_models]

    async def create_many(self, links: list[LinkEntity]) -> list[LinkEntity]:
        async with self.session_factory() as session:
            link_models: list[LinkModel] = [self._to_orm(link) for link in links]

            session.add_all(link_models)

            await session.commit()

            return [self._from_orm(link_model) for link_model in link_models]

    async def get_existing_links(self, urls: list[str]) -> list[str]:
        async with self.session_factory() as session:
            link_models = (
                await session.execute(
                    select(self.__model.url)
                    .filter(self.__model.url.in_(urls)),
                )
            )
            return list(link_models.scalars().all())

    @staticmethod
    def _to_orm(link_entity: LinkEntity) -> LinkModel:
        """Преобразует доменную сущность в ORM модель."""
        return LinkModel(
            url=link_entity.url,
            virus_total=link_entity.virus_total,
        )

    @staticmethod
    def _from_orm(link_model: LinkModel) -> LinkEntity:
        """Преобразует ORM модель в доменную сущность."""
        return LinkEntity(
            id=link_model.id,
            url=link_model.url,
            virus_total=link_model.virus_total,
            updated_at=link_model.updated_at,
        )
