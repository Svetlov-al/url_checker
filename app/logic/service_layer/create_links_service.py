from dataclasses import dataclass

from adapters.repository import AbstractRepository
from dtos.create_links_dto import CreateLinksDTO

from domain.entities.link_entity import LinkEntity
from infra.broker.kafka import KafkaMessageBroker


@dataclass
class CreateLinksService:
    repo: AbstractRepository
    kafka_broker: KafkaMessageBroker

    async def run(self, params: CreateLinksDTO) -> int:
        links = [LinkEntity(url=link) for link in params.links]

        # => Проверяем существующие ссылки
        existing_links = await self.repo.get_existing_links([link.url for link in links])

        # => Фильтруем новые ссылки
        new_links = [link for link in links if link.url not in existing_links]

        await self.kafka_broker.publish_message(
            key=b"test",
            topic='links',
            value=links[0].url.encode(),
        )

        if not new_links:
            return 0

        await self.repo.create_many(new_links)

        return len(new_links)
