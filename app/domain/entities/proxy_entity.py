from dataclasses import dataclass


@dataclass(frozen=True)
class ProxyEntity:
    id: int  # noqa: A003
    url: str
    is_active: bool
