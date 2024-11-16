from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from app.adapters.orm.result import ResultStatus


@dataclass
class AbstractMessageChecker(ABC):
    @abstractmethod
    async def process_batch(self, messages: list[bytes]) -> dict[int, ResultStatus]:
        raise NotImplementedError

    @abstractmethod
    async def _process_message(self, message: bytes, results: dict) -> None:
        raise NotImplementedError
