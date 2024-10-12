from pydantic import BaseModel


class CreateUrlRequestSchema(BaseModel):
    links: list[str]
