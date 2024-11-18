import logging

from orjson import orjson


logger = logging.getLogger(__name__)


def _prepare_messages(messages: list[bytes]) -> dict[str, str]:
    links = {}
    for message in messages:
        try:
            message_data = orjson.loads(message)
            links.update({str(k): v for k, v in message_data.items()})
        except Exception as e:
            logger.error(f"Ошибка при разборе сообщения: {e}")

    return links
