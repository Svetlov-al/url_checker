from dataclasses import dataclass

import orjson
from app.adapters.repositories.link_repository import AbstractLinkRepository
from app.domain.entities.link_entity import LinkEntity
from app.dtos.create_links_dto import CreateLinksDTO
from app.infra.broker.base import BaseBroker
from app.logic.service_layer.helpers.normalize_url import normalize_url


@dataclass
class CreateLinksService:
    repo: AbstractLinkRepository
    redis_broker: BaseBroker

    async def run(self, params: CreateLinksDTO) -> int:
        normalized_links = [normalize_url(url) for url in params.links]

        links = [LinkEntity(url=link) for link in normalized_links]

        # => Проверяем существующие ссылки
        existing_links = await self.repo.get_existing_links([link.url for link in links])

        # => Фильтруем новые ссылки
        new_links = [link for link in links if link not in existing_links]

        if not new_links:
            return 0

        created_links = await self.repo.create_many(new_links)

        # => Подготавливаем сообщения для отправки в очереди
        messages = [orjson.dumps({str(link.id): link.url}) for link in created_links]

        await self.redis_broker.publish_batch("virus_total", messages)
        await self.redis_broker.publish_batch("abusive_exp", messages)

        return len(created_links)
