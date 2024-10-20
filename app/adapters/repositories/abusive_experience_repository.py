import abc
import logging
from collections.abc import Callable
from typing import AsyncContextManager

from app.adapters.orm.abusive_experience import AbusiveExperienceModel
from app.domain.entities.abusive_experience_entity import AbusiveExperienceEntity
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractAbusiveExperienceRepository(abc.ABC):
    def __init__(self, session_factory: Callable[..., AsyncContextManager[AsyncSession]]):
        self.session_factory = session_factory

    @abc.abstractmethod
    async def add(self, result: AbusiveExperienceEntity) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_link_id(self, link_id: int) -> AbusiveExperienceEntity | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_list(self, link_ids: list[int]) -> list[AbusiveExperienceEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def create_many(self, results: list[AbusiveExperienceEntity]) -> list[AbusiveExperienceEntity]:
        raise NotImplementedError


logger = logging.getLogger(__name__)


class AbusiveExperienceRepository(AbstractAbusiveExperienceRepository):
    def __init__(self, session_factory: Callable[..., AsyncContextManager[AsyncSession]]) -> None:
        super().__init__(session_factory)
        self.__model = AbusiveExperienceModel

    async def add(self, result: AbusiveExperienceEntity) -> None:
        async with self.session_factory() as session:
            session.add(self._to_orm(result))
            await session.commit()

    async def get_by_link_id(self, link_id: int) -> AbusiveExperienceEntity | None:
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

    async def get_list(self, link_ids: list[int]) -> list[AbusiveExperienceEntity]:
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

    async def create_many(self, results: list[AbusiveExperienceEntity]) -> list[AbusiveExperienceEntity]:
        async with self.session_factory() as session:
            result_models: list[AbusiveExperienceModel] = [self._to_orm(result) for result in results]

            for result_model in result_models:
                stmt = insert(AbusiveExperienceModel).values(
                    link_id=result_model.link_id,
                    result=result_model.result,
                ).on_conflict_do_update(
                    index_elements=['link_id'],
                    set_={'result': result_model.result},
                )
                try:
                    await session.execute(stmt)
                except IntegrityError as e:
                    logger.error(
                        f"[AbusiveExperienceModel]: Ошибка при вставке для link_id {result_model.link_id}: {e.orig}",
                    )

            await session.commit()

            return [self._from_orm(result) for result in result_models]

    @staticmethod
    def _to_orm(result_entity: AbusiveExperienceEntity) -> AbusiveExperienceModel:
        """Преобразует доменную сущность в ORM модель."""
        return AbusiveExperienceModel(
            link_id=result_entity.link_id,
            result=result_entity.result,
        )

    @staticmethod
    def _from_orm(result_model: AbusiveExperienceModel) -> AbusiveExperienceEntity:
        """Преобразует ORM модель в доменную сущность."""
        return AbusiveExperienceEntity(
            link_id=result_model.link_id,
            result=result_model.result,
        )
