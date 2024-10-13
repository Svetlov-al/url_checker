from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from aiokafka import ConsumerRecord


@dataclass
class IMessageProcessor(ABC):
    @abstractmethod
    async def process_batch(self, api_key: str, messages: list[ConsumerRecord]) -> None:
        raise NotImplementedError
