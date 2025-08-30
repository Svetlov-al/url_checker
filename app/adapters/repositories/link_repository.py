import abc

from app.adapters.orm.base_link import LinkModel
from app.database.mixins import QueryMixin
from app.domain.entities.link_entity import LinkEntity
from app.logic.service_layer.helpers.message import Message
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class AbstractLinkRepository(abc.ABC):
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


class LinkRepository(AbstractLinkRepository, QueryMixin):

    async def add(self, link: LinkEntity) -> None:
        self.session.add(self._to_orm(link))
        await self.session.commit()

    async def get(self, url: str) -> LinkEntity | None:
        link_model = (
            (
                await self.session.execute(
                    select(LinkModel)
                    .options(
                        selectinload(LinkModel.result),
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
        link_models = (
            await self.session.execute(
                select(LinkModel)
                .options(
                    selectinload(LinkModel.result),
                )
                .limit(limit)
                .offset(offset),
            )
        )
        link_models = link_models.scalars().all()

        return [self._from_orm(link_model) for link_model in link_models]

    async def create_many(self, links: list[LinkEntity]) -> list[Message]:
        link_models: list[LinkModel] = [self._to_orm(link) for link in links]

        self.session.add_all(link_models)

        await self.session.commit()

        return [Message(id=link_model.id, url=link_model.url) for link_model in link_models]

    async def get_existing_links(self, urls: list[str]) -> list[LinkEntity]:
        link_models = (
            await self.session.execute(
                select(LinkModel)
                .options(
                    selectinload(LinkModel.result),
                )
                .filter(LinkModel.url.in_(urls)),
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
