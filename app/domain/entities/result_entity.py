from dataclasses import dataclass
from datetime import datetime

from app.adapters.orm.result import ResultStatus


@dataclass
class ResultEntity:
    link_id: int
    virus_total: ResultStatus | None = None
    abusive_experience: ResultStatus | None = None
    complete_date: datetime | None = None
