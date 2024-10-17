import logging
from dataclasses import dataclass

from app.infra.broker.base import BaseBroker
from redis.asyncio import Redis


logger = logging.getLogger(__name__)


@dataclass
class RedisMessageBroker(BaseBroker):
    redis: Redis

    async def publish_message(self, queue_name: str, value: bytes):
        try:
            await self.redis.lpush(queue_name, value)
        except Exception as e:
            logger.error(
                f"[Redis]: Ошибка при отправке сообщения:\n"
                f"Error: {e}",
            )

    async def publish_batch(self, queue_name: str, messages: list[bytes]) -> None:
        try:
            pipeline = self.redis.pipeline()
            for message in messages:
                pipeline.lpush(queue_name, message)
            await pipeline.execute()
        except Exception as e:
            logger.error(
                f"[Redis]: Ошибка при отправке сообщений:\n"
                f"Error: {e}",
            )

    async def read_messages(self, queue_name: str, count: int = 1) -> list[bytes]:
        """Читать сообщения из очереди с гарантией FIFO."""
        try:
            messages = await self.redis.lpop(queue_name, count)
            return messages
        except Exception as e:
            logger.error(
                f"[Redis]: Ошибка при чтении сообщений:\n"
                f"Error: {e}",
            )
            return []
