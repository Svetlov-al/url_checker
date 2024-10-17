from dataclasses import dataclass


@dataclass(frozen=True)
class GetLinksDTO:
    urls: list[str]
