import logging
from dataclasses import dataclass

from aiokafka.producer import AIOKafkaProducer

from infra.broker.base import BaseProducer


logger = logging.getLogger(__name__)


@dataclass
class KafkaMessageProducer(BaseProducer):
    producer: AIOKafkaProducer

    async def publish_message(self, key: bytes, topic: str, value: bytes):
        await self.start()
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
            await self.close()

    async def publish_batch(self, topic: str, key: bytes, messages: list[bytes]):
        await self.start()
        try:
            for message in messages:
                await self.producer.send(
                    topic=topic,
                    key=key,
                    value=message,
                )
        except Exception as e:
            logger.error(
                f"[Kafka]: Ошибка при отправке сообщения:\n"
                f"Erro: {e}",
            )
        finally:
            await self.close()

    async def close(self):
        await self.producer.stop()

    async def start(self):
        await self.producer.start()
