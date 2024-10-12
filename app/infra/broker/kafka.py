import logging
from dataclasses import dataclass
from typing import AsyncIterator

import orjson
from aiokafka import AIOKafkaConsumer
from aiokafka.producer import AIOKafkaProducer

from infra.broker.base import BaseMessageBroker


logger = logging.getLogger(__name__)


@dataclass
class KafkaMessageBroker(BaseMessageBroker):
    producer: AIOKafkaProducer
    consumer: AIOKafkaConsumer

    async def publish_message(self, key: bytes, topic: str, value: bytes):
        await self.producer.start()
        try:
            await self.producer.send(
                topic=topic,
                key=key,
                value=value,
            )
        except Exception as e:
            logger.error(
                f"[Kafka]: Ошибка при отправке сообщения:\n"
                f"Erro: {e}",
            )
        finally:
            await self.producer.stop()

    async def start_consuming(self, topic: str) -> AsyncIterator[dict]:
        self.consumer.subscribe(topics=[topic])

        async for message in self.consumer:
            yield orjson.loads(message.value)

    async def stop_consuming(self) -> None:
        self.consumer.unsubscribe()

    async def close(self):
        await self.consumer.stop()
        await self.producer.stop()

    async def start(self):
        await self.producer.start()
        await self.consumer.start()
