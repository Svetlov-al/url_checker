from pydantic import BaseModel


class GetLinksRequestSchema(BaseModel):
    urls: list[str]
