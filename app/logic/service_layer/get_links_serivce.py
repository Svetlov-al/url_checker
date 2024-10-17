from dataclasses import dataclass

from app.adapters.repositories.link_repository import AbstractLinkRepository
from app.domain.entities.link_entity import LinkEntity
from app.infra.filters.get_all_links_infra_filters import GetAllLinksInfraFilters


@dataclass
class GetLinksService:
    repo: AbstractLinkRepository

    async def run(self, filters: GetAllLinksInfraFilters) -> tuple[list[LinkEntity], int]:
        result = await self.repo.get_list(
            limit=filters.limit,
            offset=filters.offset,
        )

        return result, len(result)
