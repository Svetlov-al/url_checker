from dataclasses import dataclass


@dataclass(frozen=True)
class GetLinkDTO:
    url: str
