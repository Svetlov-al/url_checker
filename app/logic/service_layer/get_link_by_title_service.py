from dataclasses import dataclass

from app.adapters.repositories.link_repository import AbstractLinkRepository
from app.domain.entities.link_entity import LinkEntity
from app.logic.service_layer.helpers.normalize_url import normalize_url


@dataclass
class GetLinksByDomainListService:
    repo: AbstractLinkRepository

    async def run(self, urls: list[str]) -> list[LinkEntity]:
        urls = [normalize_url(link) for link in urls]
        results = await self.repo.get_existing_links(
            urls=urls,
        )

        return results
