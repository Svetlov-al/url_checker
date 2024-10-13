from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass


@dataclass
class BaseProducer(ABC):
    @abstractmethod
    async def start(self):
        raise NotImplementedError

    @abstractmethod
    async def close(self):
        raise NotImplementedError

    @abstractmethod
    async def publish_message(self, key: str, topic: str, value: bytes) -> None:
        raise NotImplementedError

    @abstractmethod
    async def publish_batch(self, topic: str, key: bytes, messages: list[bytes]) -> None:
        raise NotImplementedError


class BaseConsumer(ABC):
    @abstractmethod
    async def start(self):
        raise NotImplementedError

    @abstractmethod
    async def close(self):
        raise NotImplementedError

    @abstractmethod
    async def start_consuming(self, topic: str, batch_size: int, max_attempts: int) -> list:
        raise NotImplementedError
