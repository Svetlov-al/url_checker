from dataclasses import dataclass

from adapters.repository import AbstractRepository

from domain import model
from infra.filters.get_all_links_infra_filters import GetAllLinksInfraFilters


@dataclass
class GetGoodLinksService:
    repo: AbstractRepository

    async def run(self, filters: GetAllLinksInfraFilters) -> tuple[list[model.Link], int]:
        result = await self.repo.get_list(
            limit=filters.limit,
            offset=filters.offset,
            virus_total=filters.virus_total,
        )

        return result, len(result)
