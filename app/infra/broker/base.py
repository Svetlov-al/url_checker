from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass


@dataclass
class BaseBroker(ABC):

    @abstractmethod
    async def publish_message(self, queue_name: str, message: bytes) -> None:
        raise NotImplementedError

    @abstractmethod
    async def publish_batch(self, queue_name: str, messages: list[bytes]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def read_messages(self, queue_name: str, count: int = 1) -> list[bytes]:
        raise NotImplementedError
