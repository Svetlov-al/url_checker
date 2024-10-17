from dataclasses import dataclass


@dataclass
class AbusiveExperienceEntity:
    link_id: int
    url: str
    result: bool
