from dataclasses import dataclass
from datetime import datetime


@dataclass
class LinkEntity:
    url: str
    id: int | None = None  # noqa: A003
    virus_total: bool = None
    updated_at: datetime | None = None
