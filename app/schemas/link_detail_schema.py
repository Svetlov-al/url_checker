from datetime import datetime

from app.domain.entities.link_entity import LinkEntity
from pydantic import BaseModel


class LinkDetailSchema(BaseModel):
    id: int  # noqa: A003
    url: str
    virus_total: bool | None
    abusive_exp: bool | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, link: LinkEntity) -> 'LinkDetailSchema':
        return cls(
            id=link.id,
            url=link.url,
            virus_total=link.virus_total,
            abusive_exp=link.abusive_exp,
            created_at=link.created_at,
            updated_at=link.updated_at,
        )
