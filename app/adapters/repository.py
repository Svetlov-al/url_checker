import abc
from collections.abc import Callable
from contextlib import AbstractContextManager

from adapters.orm import LinkModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain import model


class AbstractRepository(abc.ABC):
    __model = None

    @abc.abstractmethod
    async def add(self, link: model.Link):
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, url: str) -> model.Link | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_list(self, limit: int, offset: int, virus_total: bool) -> list[model.Link]:
        raise NotImplementedError

    @abc.abstractmethod
    async def create_many(self, links: list[model.Link]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_existing_links(self, urls: list[str]) -> list[str]:
        raise NotImplementedError


class LinkRepository(AbstractRepository):
    __model = LinkModel

    def __init__(self, session_factory: Callable[..., AbstractContextManager[AsyncSession]]) -> None:
        self.session_factory = session_factory

    async def add(self, link: model.Link) -> None:
        async with self.session_factory() as session:
            session.add(link.to_domain())
            await session.commit()

    async def get(self, url: str) -> model.Link | None:
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

            return model.Link.from_domain(link_model)

    async def get_list(self, limit: int, offset: int, virus_total: bool) -> list[model.Link]:
        async with self.session_factory() as session:
            results = (
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
            return [model.Link.from_domain(link) for link in results]

    async def create_many(self, links: list[model.Link]) -> None:
        async with self.session_factory() as session:
            link_models = [link.to_domain() for link in links]
            session.add_all(link_models)
            await session.commit()

    async def get_existing_links(self, urls: list[str]) -> list[str]:
        async with self.session_factory() as session:
            results = (
                await session.execute(
                    select(self.__model.url)
                    .filter(self.__model.url.in_(urls)),
                )
            )
            return list(results.scalars().all())
