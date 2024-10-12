from pydantic import BaseModel
from schemas.link_detail_schema import LinkDetailSchema


class LinksResponseSchema(BaseModel):
    count: int
    limit: int
    offset: int
    items: list[LinkDetailSchema]
