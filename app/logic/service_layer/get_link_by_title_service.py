from dataclasses import dataclass

from app.adapters.repositories.link_repository import AbstractLinkRepository
from app.domain.entities.link_entity import LinkEntity
from app.dtos.get_links_dto import GetLinksDTO


@dataclass
class GetLinksByDomainListService:
    repo: AbstractLinkRepository

    async def run(self, params: GetLinksDTO) -> list[LinkEntity]:
        results = await self.repo.get_existing_links(
            urls=params.urls,
        )

        return results
