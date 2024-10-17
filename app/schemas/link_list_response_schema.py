from app.schemas.link_detail_schema import LinkDetailSchema
from pydantic import BaseModel


class LinksResponseSchema(BaseModel):
    count: int
    limit: int
    offset: int
    items: list[LinkDetailSchema]
