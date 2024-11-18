from dataclasses import (
    dataclass,
    field,
)

from app.adapters.orm.proxy import ProxyModel
from app.domain.entities.proxy_entity import ProxyEntity


@dataclass
class APIKeyEntity:
    key_id: int
    api_key: str
    daily_limit: int
    used_limit: int
    is_valid: bool = True
    proxies: list[ProxyEntity] = field(default_factory=list)
    links_to_process: list[dict[str, str]] = field(default_factory=list)
    delay: int | None = None

    @property
    def limit(self) -> int:
        return self.daily_limit - self.used_limit

    def get_proxy_url(self) -> str:
        return next((proxy.url for proxy in self.proxies), "")

    def add_proxies(self, proxy_models: list[ProxyModel]) -> None:
        if not proxy_models:
            return

        for proxy in proxy_models:
            if not proxy.is_active:
                continue

            existing_proxy = next(
                (p for p in self.proxies if p.id == proxy.id), None,
            )
            if not existing_proxy:
                self.proxies.append(
                    ProxyEntity(
                        id=proxy.id,
                        url=proxy.url,
                        is_active=proxy.is_active,
                    ),
                )

    def add_link(self, link: dict[str, str]) -> None:
        """Добавляет ссылку в список для обработки этим ключом."""
        self.links_to_process.append(link)
