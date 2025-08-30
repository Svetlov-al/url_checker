from dataclasses import dataclass
from datetime import (
    datetime,
    timedelta,
)

import orjson
from app.adapters.repositories.link_repository import AbstractLinkRepository
from app.adapters.repositories.result_repository import AbstractResultRepository
from app.domain.entities.link_entity import LinkEntity
from app.infra.broker.base import BaseBroker
from app.logic.service_layer.helpers.normalize_url import normalize_url


@dataclass
class CreateLinksService:
    repo: AbstractLinkRepository
    result_repo: AbstractResultRepository
    redis_broker: BaseBroker

    async def run(self, links: list[str]) -> int:
        normalized_links = [normalize_url(url) for url in links]

        links = [LinkEntity(url=link) for link in normalized_links]

        # => Проверяем существующие ссылки
        existing_links = await self.repo.get_existing_links([link.url for link in links])

        # => Фильтруем новые ссылки
        threshold_date = datetime.now() - timedelta(days=10)

        new_links = [
            link for link in links
            if link not in existing_links
        ]

        old_links_with_results = [
            link for link in existing_links
            if link.complete_date and link.complete_date <= threshold_date
        ]

        if not new_links and not old_links_with_results:
            return 0

        link_ids_to_update = [link.id for link in old_links_with_results]

        created_links = await self.repo.create_many(new_links)
        updated_results = await self.result_repo.reset_results(link_ids_to_update)

        all_messages = created_links + updated_results

        # => Подготавливаем сообщения для отправки в очереди
        messages = [orjson.dumps({str(link.id): link.url}) for link in all_messages]

        await self.redis_broker.publish_batch("virus_total", messages)
        await self.redis_broker.publish_batch("abusive_exp", messages)

        return len(all_messages)
