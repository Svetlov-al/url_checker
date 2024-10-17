from dataclasses import dataclass


@dataclass
class VirusTotalEntity:
    link_id: int
    url: str
    result: bool
