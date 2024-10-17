import abc
from collections.abc import Callable
from typing import AsyncContextManager

from app.adapters.orm.virus_total import VirusTotalModel
from app.domain.entities.virus_total_entity import VirusTotalEntity
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractVirusTotalRepository(abc.ABC):
    __model = None

    @abc.abstractmethod
    async def add(self, result: VirusTotalEntity) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_link_id(self, link_id: int) -> VirusTotalEntity | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def create_many(self, results: list[VirusTotalEntity]) -> list[VirusTotalEntity]:
        raise NotImplementedError


class VirusTotalRepository(AbstractVirusTotalRepository):
    __model = VirusTotalModel

    def __init__(self, session_factory: Callable[..., AsyncContextManager[AsyncSession]]) -> None:
        self.session_factory = session_factory

    async def add(self, result: VirusTotalEntity) -> None:
        async with self.session_factory() as session:
            session.add(self._to_orm(result))
            await session.commit()

    async def get_by_link_id(self, link_id: int) -> VirusTotalEntity | None:
        async with self.session_factory() as session:
            result = (
                (
                    await session.execute(
                        select(self.__model)
                        .filter_by(
                            link_id=link_id,
                        ),
                    )
                )
                .scalars()
                .one_or_none()
            )
            if not result:
                return None

            return self._from_orm(result)

    async def get_list(self, link_ids: list[int]) -> list[VirusTotalEntity]:
        async with self.session_factory() as session:
            results = (
                (
                    await session.execute(
                        select(self.__model)
                        .filter(self.__model.link_id.in_(link_ids)),
                    )
                )
                .scalars()
                .all()
            )
            return [self._from_orm(result) for result in results]

    async def create_many(self, results: list[VirusTotalEntity]) -> list[VirusTotalEntity]:
        async with self.session_factory() as session:
            result_models: list[VirusTotalModel] = [self._to_orm(result) for result in results]

            for result_model in result_models:
                stmt = insert(VirusTotalModel).values(
                    link_id=result_model.link_id,
                    result=result_model.result,
                ).on_conflict_do_update(
                    index_elements=['link_id'],
                    set_={'result': result_model.result},
                )
                await session.execute(stmt)

            await session.commit()

            return [self._from_orm(result) for result in result_models]

    @staticmethod
    def _to_orm(result_entity: VirusTotalEntity) -> VirusTotalModel:
        """Преобразует доменную сущность в ORM модель."""
        return VirusTotalModel(
            link_id=result_entity.link_id,
            result=result_entity.result,
        )

    @staticmethod
    def _from_orm(result_model: VirusTotalModel) -> VirusTotalEntity:
        """Преобразует ORM модель в доменную сущность."""
        return VirusTotalEntity(
            link_id=result_model.link_id,
            url=result_model.link.url,
            result=result_model.result,
        )
