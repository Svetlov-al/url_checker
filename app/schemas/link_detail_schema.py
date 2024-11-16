from datetime import datetime

from app.domain.entities.link_entity import LinkEntity
from pydantic import BaseModel


class LinkDetailSchema(BaseModel):
    id: int  # noqa: A003
    url: str
    virus_total: str
    abusive_exp: str
    created_at: datetime
    updated_at: datetime
    complete_date: datetime

    @classmethod
    def from_entity(cls, link: LinkEntity) -> 'LinkDetailSchema':
        return cls(
            id=link.id,
            url=link.url,
            virus_total=link.virus_total,
            abusive_exp=link.abusive_exp,
            created_at=link.created_at,
            updated_at=link.updated_at,
            complete_date=link.complete_date,
        )
