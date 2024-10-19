from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

import httpx


@dataclass
class IMessageProcessor(ABC):
    @abstractmethod
    async def process_batch(self, messages: list[bytes]) -> dict[int, bool]:
        raise NotImplementedError

    @abstractmethod
    async def _process_message(self, client: httpx.AsyncClient, message: bytes, results: dict) -> None:
        raise NotImplementedError
