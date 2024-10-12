from pydantic import BaseModel

from infra.filters.get_all_links_infra_filters import GetAllLinksInfraFilters


class GetAllLinksFilters(BaseModel):
    limit: int = 10
    offset: int = 0

    def to_infra(self):
        return GetAllLinksInfraFilters(limit=self.limit, offset=self.offset)
