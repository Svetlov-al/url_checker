from dataclasses import dataclass
from datetime import datetime

from adapters.orm import LinkModel


@dataclass
class LinkEntity:
    url: str
    id: int | None = None  # noqa: A003
    virus_total: bool = False
    updated_at: datetime | None = None

    @classmethod
    def from_domain(cls, link_model: LinkModel) -> "LinkEntity":
        """Создает объект LinkEntity из модели SQLAlchemy."""
        return cls(
            id=link_model.id,
            url=link_model.url,
            virus_total=link_model.virus_total,
            updated_at=link_model.updated_at,
        )

    def to_domain(self) -> LinkModel:
        """Преобразует объект LinkEntity в модель SQLAlchemy."""
        return LinkModel(
            url=self.url,
            virus_total=self.virus_total,
        )
