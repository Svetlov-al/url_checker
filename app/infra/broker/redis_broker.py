import logging
from dataclasses import dataclass

from app.infra.broker.base import BaseBroker
from redis.asyncio import Redis


logger = logging.getLogger(__name__)


@dataclass
class RedisMessageBroker(BaseBroker):
    redis: Redis

    async def publish_message(self, queue_name: str, message: bytes):
        try:
            await self.redis.rpush(queue_name, message)
        except Exception as e:
            logger.error(
                f"[Redis]: Ошибка при отправке сообщения {message}:\n"
                f"Error: {e}",
            )

    async def publish_batch(self, queue_name: str, messages: list[bytes]) -> None:
        try:
            pipeline = self.redis.pipeline()
            for message in messages:
                pipeline.rpush(queue_name, message)
            await pipeline.execute()
        except Exception as e:
            logger.error(
                f"[Redis]: Ошибка при отправке сообщений: {messages}\n"
                f"Error: {e}",
            )

    async def read_messages(self, queue_name: str, count: int = 1) -> list[bytes]:
        """Читать сообщения из очереди с гарантией FIFO."""
        try:
            pipeline = self.redis.pipeline()
            for _ in range(count):
                pipeline.lpop(queue_name)
            messages = await pipeline.execute()
            return [msg for msg in messages if msg]
        except Exception as e:
            logger.error(
                f"[Redis]: Ошибка при чтении сообщений:\n"
                f"Error: {e}",
            )
            return []
