from dataclasses import dataclass

from app.adapters.repositories.link_repository import AbstractLinkRepository
from app.domain.entities.link_entity import LinkEntity
from app.dtos.get_links_dto import GetLinksDTO
from app.logic.service_layer.helpers.normalize_url import normalize_url


@dataclass
class GetLinksByDomainListService:
    repo: AbstractLinkRepository

    async def run(self, params: GetLinksDTO) -> list[LinkEntity]:
        urls = [normalize_url(link) for link in params.urls]
        results = await self.repo.get_existing_links(
            urls=urls,
        )

        return results
