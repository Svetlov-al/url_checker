import asyncio
import logging
from dataclasses import dataclass

from aiokafka import (
    AIOKafkaConsumer,
    ConsumerRecord,
)

from infra.broker.base import BaseConsumer


logger = logging.getLogger(__name__)


@dataclass
class KafkaMessageConsumer(BaseConsumer):
    consumer: AIOKafkaConsumer

    async def start_consuming(
        self,
        topic: str,
        batch_size: int,
        max_attempts: int = 10,
    ) -> list[ConsumerRecord]:

        messages: list[ConsumerRecord] = []

        await self.start()

        try:
            attempts = 0
            while attempts < max_attempts:
                # => Получаем сообщения из очереди
                fetched_messages = await self.consumer.getmany(timeout_ms=500, max_records=batch_size)

                if not fetched_messages:
                    attempts += 1
                    logger.warning(
                        f"[Kafka]: Нет новых сообщений! Попытка: {attempts}/{max_attempts}",
                    )
                    await asyncio.sleep(0.1)
                    continue

                offsets_to_commit = {}
                for tp, records in fetched_messages.items():
                    if records:
                        # => Определяем количество сообщений, которое можно добавить в текущий батч
                        remaining_capacity = batch_size - len(messages)

                        if remaining_capacity > 0:
                            # => Добавляем только те сообщения, которые помещаются в батч
                            messages.extend(records[:remaining_capacity])
                            offsets_to_commit[tp] = records[min(len(records), remaining_capacity) - 1].offset + 1

                        if len(messages) >= batch_size:
                            break

                if offsets_to_commit:
                    await self.consumer.commit(offsets_to_commit)

                if len(messages) >= batch_size:
                    break

        except Exception as e:
            logger.error(
                f"[Kafka]: Ошибка подписки на топик {topic}:\n"
                f"Error: {str(e)}",
            )
        finally:
            await self.close()
            logger.info(
                f"[Kafka]: Сбор сообщений завершен! Собрано сообщений: {len(messages)}",
            )

        return messages

    async def close(self):
        await self.consumer.stop()

    async def start(self):
        await self.consumer.start()
