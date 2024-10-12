from dataclasses import dataclass

from adapters.repository import AbstractRepository

from domain.entities.link_entity import LinkEntity
from infra.filters.get_all_links_infra_filters import GetAllLinksInfraFilters


@dataclass
class GetGoodLinksService:
    repo: AbstractRepository

    async def run(self, filters: GetAllLinksInfraFilters) -> tuple[list[LinkEntity], int]:
        result = await self.repo.get_list(
            limit=filters.limit,
            offset=filters.offset,
            virus_total=filters.virus_total,
        )

        return result, len(result)
