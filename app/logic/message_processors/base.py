from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass


@dataclass
class IMessageProcessor(ABC):
    @abstractmethod
    async def process_batch(self, api_key: str, messages: list[str]) -> dict[int, bool]:
        raise NotImplementedError
