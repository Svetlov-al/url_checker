import logging

from app.domain.entities.api_key_entity import APIKeyEntity


logger = logging.getLogger(__name__)


def _distribute_links_among_keys(
    api_keys: list[APIKeyEntity],
    links: dict[str, str],
    key_limits: dict[str, int],
) -> None:
    """Распределяет ссылки между ключами и добавляет их в `APIKeyEntity`."""
    # => Создаём очередь ключей с лимитами
    keys_with_limits = [
        (key, key_limits[key.api_key]) for key in api_keys if key_limits[key.api_key] > 0
    ]

    link_items = list(links.items())
    link_index = 0
    total_links = len(link_items)

    while link_index < total_links and keys_with_limits:
        keys_with_limits.sort(key=lambda x: x[1], reverse=True)

        for i, (key_entity, limit) in enumerate(keys_with_limits):
            if limit > 0 and link_index < total_links:
                link_id, link_url = link_items[link_index]
                # => Добавляем ссылку для обработки для ключа
                key_entity.add_link({link_id: link_url})
                link_index += 1
                keys_with_limits[i] = (key_entity, limit - 1)

        keys_with_limits = [
            (key_entity, limit) for key_entity, limit in keys_with_limits if limit > 0
        ]
