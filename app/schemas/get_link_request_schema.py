from pydantic import BaseModel


class GetLinkRequestSchema(BaseModel):
    url: str
