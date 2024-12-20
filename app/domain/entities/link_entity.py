from dataclasses import dataclass
from datetime import datetime


@dataclass
class LinkEntity:
    url: str
    id: int | None = None  # noqa: A003
    virus_total: str | None = None
    abusive_exp: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    complete_date: datetime | None = None

    def __eq__(self, other: "LinkEntity") -> bool:
        if self.url == other.url:
            return True
        return False
