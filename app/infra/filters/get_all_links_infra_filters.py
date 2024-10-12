from dataclasses import dataclass


@dataclass
class GetAllLinksInfraFilters:
    limit: int
    offset: int
    virus_total: bool = False
