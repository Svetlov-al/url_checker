from datetime import datetime

from pydantic import BaseModel

from domain.entities.link_entity import LinkEntity


class LinkDetailSchema(BaseModel):
    id: int  # noqa: A003
    url: str
    virus_total: bool
    updated_at: datetime

    @classmethod
    def from_entity(cls, link: LinkEntity) -> 'LinkDetailSchema':
        return cls(
            id=link.id,
            url=link.url,
            virus_total=link.virus_total,
            updated_at=link.updated_at,
        )