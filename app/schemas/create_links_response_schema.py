from pydantic import BaseModel


class CreateLinksResponseSchema(BaseModel):
    message: str
    count: int
