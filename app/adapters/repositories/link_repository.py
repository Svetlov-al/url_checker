import abc
from collections.abc import Callable
from typing import AsyncContextManager

from app.adapters.orm.base_link import LinkModel
from app.domain.entities.link_entity import LinkEntity
from app.logic.service_layer.helpers.message import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class AbstractLinkRepository(abc.ABC):
    def __init__(self, session_factory: Callable[..., AsyncContextManager[AsyncSession]]):
        self.session_factory = session_factory

    @abc.abstractmethod
    async def add(self, link: LinkEntity) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, url: str) -> LinkEntity | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_list(self, limit: int, offset: int) -> list[LinkEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def create_many(self, links: list[LinkEntity]) -> list[Message]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_existing_links(self, urls: list[str]) -> list[LinkEntity]:
        raise NotImplementedError


class LinkRepository(AbstractLinkRepository):
    def __init__(self, session_factory: Callable[..., AsyncContextManager[AsyncSession]]) -> None:
        super().__init__(session_factory)
        self.__model = LinkModel

    async def add(self, link: LinkEntity) -> None:
        async with self.session_factory() as session:
            session.add(self._to_orm(link))
            await session.commit()

    async def get(self, url: str) -> LinkEntity | None:
        async with self.session_factory() as session:
            link_model = (
                (
                    await session.execute(
                        select(self.__model)
                        .options(
                            selectinload(self.__model.result),
                        )
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

    async def get_list(self, limit: int, offset: int) -> list[LinkEntity]:
        async with self.session_factory() as session:
            link_models = (
                await session.execute(
                    select(self.__model)
                    .options(
                        selectinload(self.__model.result),
                    )
                    .limit(limit)
                    .offset(offset),
                )
            )
            link_models = link_models.scalars().all()

            return [self._from_orm(link_model) for link_model in link_models]

    async def create_many(self, links: list[LinkEntity]) -> list[Message]:
        async with self.session_factory() as session:
            link_models: list[LinkModel] = [self._to_orm(link) for link in links]

            session.add_all(link_models)

            await session.commit()

            return [Message(id=link_model.id, url=link_model.url) for link_model in link_models]

    async def get_existing_links(self, urls: list[str]) -> list[LinkEntity]:
        async with self.session_factory() as session:
            link_models = (
                await session.execute(
                    select(self.__model)
                    .options(
                        selectinload(self.__model.result),
                    )
                    .filter(self.__model.url.in_(urls)),
                )
            )
            return [self._from_orm(link) for link in link_models.scalars().all()]

    @staticmethod
    def _to_orm(link_entity: LinkEntity) -> LinkModel:
        """Преобразует доменную сущность в ORM модель."""
        return LinkModel(
            url=link_entity.url,
        )

    @staticmethod
    def _from_orm(link_model: LinkModel) -> LinkEntity:
        """Преобразует ORM модель в доменную сущность."""
        return LinkEntity(
            id=link_model.id,
            url=link_model.url,
            virus_total=(
                link_model.result.virus_total if link_model.result else None
            ),
            abusive_exp=(
                link_model.result.abusive_experience if link_model.result else None
            ),
            created_at=link_model.created_at,
            updated_at=link_model.updated_at,
            complete_date=link_model.result.complete_date if link_model.result else None,
        )
