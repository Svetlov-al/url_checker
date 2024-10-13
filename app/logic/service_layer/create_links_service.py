from dataclasses import dataclass

from adapters.repository import AbstractRepository
from dtos.create_links_dto import CreateLinksDTO
from orjson import orjson

from domain.entities.link_entity import LinkEntity
from infra.broker.kafka_producer import KafkaMessageProducer


@dataclass
class CreateLinksService:
    repo: AbstractRepository
    kafka_producer: KafkaMessageProducer

    async def run(self, params: CreateLinksDTO) -> int:
        links = [LinkEntity(url=link) for link in params.links]

        # => Проверяем существующие ссылки
        existing_links = await self.repo.get_existing_links([link.url for link in links])

        # => Фильтруем новые ссылки
        new_links = [link for link in links if link.url not in existing_links]

        if not new_links:
            return 0

        created_links = await self.repo.create_many(new_links)

        await self.publish_links_to_kafka(created_links)

        return len(created_links)

    async def publish_links_to_kafka(self, links: list[LinkEntity]) -> None:
        messages: list[bytes] = [
            orjson.dumps({str(link.id): link.url}) for link in links
        ]

        await self.kafka_producer.publish_batch(
            key=b"test",
            topic='links',
            messages=messages,
        )
