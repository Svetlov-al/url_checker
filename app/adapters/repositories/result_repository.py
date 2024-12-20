import abc
import logging
from collections.abc import Callable
from typing import AsyncContextManager

from app.adapters.orm.result import (
    ResultModel,
    ResultStatus,
)
from app.domain.entities.result_entity import ResultEntity
from app.logic.service_layer.helpers.message import Message
from sqlalchemy import (
    func,
    select,
    update,
)
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import case


class AbstractResultRepository(abc.ABC):
    def __init__(self, session_factory: Callable[..., AsyncContextManager[AsyncSession]]):
        self.session_factory = session_factory

    @abc.abstractmethod
    async def add(self, result: ResultEntity) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_link_id(self, link_id: int) -> ResultEntity | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_list(self, link_ids: list[int]) -> list[ResultEntity]:
        raise NotImplementedError

    async def create_or_update_abusive_experience(self, results: list[ResultEntity]) -> list[ResultEntity]:
        raise NotImplementedError

    async def create_or_update_virus_total(self, results: list[ResultEntity]) -> list[ResultEntity]:
        raise NotImplementedError

    async def reset_results(self, link_ids: list[int]) -> list[Message]:
        raise NotImplementedError


logger = logging.getLogger(__name__)


class ResultRepository(AbstractResultRepository):
    def __init__(self, session_factory: Callable[..., AsyncContextManager[AsyncSession]]) -> None:
        super().__init__(session_factory)
        self.__model = ResultModel

    async def add(self, result: ResultEntity) -> None:
        async with self.session_factory() as session:
            session.add(self._to_orm(result))
            await session.commit()

    async def get_by_link_id(self, link_id: int) -> ResultEntity | None:
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

    async def get_list(self, link_ids: list[int]) -> list[ResultEntity]:
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

    async def create_or_update_virus_total(self, results: list[ResultEntity]) -> list[ResultEntity]:
        async with self.session_factory() as session:
            result_models: list[ResultModel] = [
                self._to_orm(result, fields_to_update={"virus_total"}) for result in results
            ]

            for result_model in result_models:
                values_to_insert = {
                    "link_id": result_model.link_id,
                    "virus_total": result_model.virus_total,
                }

                stmt = insert(ResultModel).values(values_to_insert).on_duplicate_key_update(
                    virus_total=values_to_insert["virus_total"],
                    complete_date=case(
                        (ResultModel.abusive_experience != ResultStatus.WAITING, func.now()),
                        else_=ResultModel.complete_date,
                    ),
                )

                try:
                    await session.execute(stmt)
                except IntegrityError as e:
                    logger.error(
                        f"[ResultModel]: Ошибка при вставке для link_id {result_model.link_id}: {e.orig}",
                    )

            else:
                await session.commit()

        return [self._from_orm(result) for result in result_models]

    async def create_or_update_abusive_experience(self, results: list[ResultEntity]) -> list[ResultEntity]:
        async with self.session_factory() as session:
            result_models: list[ResultModel] = [
                self._to_orm(result, fields_to_update={"abusive_experience"}) for result in results
            ]

            for result_model in result_models:
                values_to_insert = {
                    "link_id": result_model.link_id,
                    "abusive_experience": result_model.abusive_experience,
                }

                stmt = insert(ResultModel).values(values_to_insert).on_duplicate_key_update(
                    abusive_experience=values_to_insert["abusive_experience"],
                    complete_date=case(
                        (ResultModel.virus_total != ResultStatus.WAITING, func.now()),
                        else_=ResultModel.complete_date,
                    ),
                )

                try:
                    await session.execute(stmt)
                except IntegrityError as e:
                    logger.error(
                        f"[ResultModel]: Ошибка при вставке для link_id {result_model.link_id}: {e.orig}",
                    )
            else:
                await session.commit()

        return [self._from_orm(result) for result in result_models]

    async def reset_results(self, link_ids: list[int]) -> list[Message]:
        async with self.session_factory() as session:
            result_models = await session.execute(
                select(self.__model)
                .where(self.__model.link_id.in_(link_ids))
                .options(joinedload(self.__model.link)),
            )
            result_models = result_models.scalars().all()

            await session.execute(
                update(self.__model)
                .where(self.__model.link_id.in_(link_ids))
                .values(
                    virus_total=ResultStatus.WAITING,
                    abusive_experience=ResultStatus.WAITING,
                    complete_date=None,
                ),
            )

            await session.commit()

        return [
            Message(id=result.link_id, url=result.link.url if result.link else None)
            for result in result_models
        ]

    @staticmethod
    def _to_orm(result_entity: ResultEntity, fields_to_update: set = None) -> ResultModel:
        """Преобразует доменную сущность в ORM модель, обновляя только
        переданные поля."""

        if fields_to_update is None:
            fields_to_update = {"virus_total", "abusive_experience"}

        result_model = ResultModel(link_id=result_entity.link_id)

        if "virus_total" in fields_to_update:
            result_model.virus_total = result_entity.virus_total

        if "abusive_experience" in fields_to_update:
            result_model.abusive_experience = result_entity.abusive_experience

        return result_model

    @staticmethod
    def _from_orm(result_model: ResultModel) -> ResultEntity:
        """Преобразует ORM модель в доменную сущность."""
        return ResultEntity(
            link_id=result_model.link_id,
            virus_total=result_model.virus_total,
            abusive_experience=result_model.abusive_experience,
            complete_date=result_model.complete_date,
        )
