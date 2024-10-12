from dataclasses import dataclass

from adapters.repository import AbstractRepository
from dtos.get_link_dto import GetLinkDTO

from domain import model
from domain.exceptions.link_not_found_exception import LinkNotFoundException


@dataclass
class GetLinkByTitleService:
    repo: AbstractRepository

    async def run(self, params: GetLinkDTO) -> model.Link:
        result = await self.repo.get(
            url=params.url,
        )
        if not result:
            raise LinkNotFoundException(f"Ссылка {params.url} не найдена в базе данных.")

        return result
