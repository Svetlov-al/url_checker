from dataclasses import dataclass


@dataclass
class ResultEntity:
    link_id: int
    virus_total: bool | None = None
    abusive_experience: bool | None = None
