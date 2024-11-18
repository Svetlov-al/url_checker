from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from app.adapters.orm.result import ResultStatus
from app.domain.entities.api_key_entity import APIKeyEntity


@dataclass
class AbstractMessageChecker(ABC):
    @abstractmethod
    async def process_batch(self) -> dict[int, ResultStatus]:
        raise NotImplementedError

    @abstractmethod
    async def _process_key(self, key: APIKeyEntity, results: dict[str, ResultStatus]) -> None:
        raise NotImplementedError

    async def _process_link(
            self,
            link_id: str,
            link: str,
            key: APIKeyEntity,
            results: dict[str, ResultStatus],
    ) -> None:
        raise NotImplementedError
