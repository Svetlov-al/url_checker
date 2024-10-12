from dataclasses import dataclass


@dataclass(frozen=True)
class CreateLinksDTO:
    links: list[str]
