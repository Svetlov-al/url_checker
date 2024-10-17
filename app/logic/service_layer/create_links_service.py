from dataclasses import dataclass
from urllib.parse import urlparse

from app.adapters.repositories.link_repository import AbstractLinkRepository
from app.domain.entities.link_entity import LinkEntity
from app.dtos.create_links_dto import CreateLinksDTO


@dataclass
class CreateLinksService:
    repo: AbstractLinkRepository

    async def run(self, params: CreateLinksDTO) -> int:
        normalized_links = [self.normalize_url(url) for url in params.links]

        links = [LinkEntity(url=link) for link in normalized_links]

        # => Проверяем существующие ссылки
        existing_links = await self.repo.get_existing_links([link.url for link in links])

        # => Фильтруем новые ссылки
        new_links = [link for link in links if link not in existing_links]

        if not new_links:
            return 0

        created_links = await self.repo.create_many(new_links)

        return len(created_links)

    @staticmethod
    def normalize_url(url: str) -> str:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc or parsed_url.path
        return domain.lower()
