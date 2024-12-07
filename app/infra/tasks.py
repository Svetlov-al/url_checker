import asyncio

from ..adapters.orm.credentials.api_keys import APIKeySourceType
from ..adapters.repositories.api_keys_repository import AbstractAPIKeyRepository
from ..adapters.repositories.result_repository import AbstractResultRepository
from ..core.constance import (
    SECONDS_IN_HOUR,
    VT_DELAY,
)
from ..domain.entities.result_entity import ResultEntity
from ..logic.message_processors.base import AbstractMessageChecker
from ..logic.service_layer.helpers.distribute_links import _distribute_links_among_keys  # noqa
from ..logic.service_layer.helpers.prepare_messages import _prepare_messages  # noqa
from .broker.base import BaseBroker
from .celery_worker import app as celery_app
from .ioc.container.application import AppContainer


@celery_app.task
def reset_keys_limit() -> None:
    """Задача на обновление ключей Каждый день сбрасывает лимит по ключам для
    запросов к API."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(reset_keys_limit_async())


@celery_app.task
def vt_validate(queue: str = 'virus_total') -> dict[int, str]:
    """Задача выгружает из очереди ссылки для обработки в системе VirusTotal
    :param queue: str = virus_total :return: dict[int, str]"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(vt_validate_async(queue))


@celery_app.task
def ae_validate(queue: str = 'abusive_exp') -> dict[int, str]:
    """Задача выгружает из очереди ссылки для обработки в системе Abusive
    Experience :param queue: str = abusive_exp :return: dict[int, str]"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(ae_validate_async(queue))


async def vt_validate_async(queue: str) -> dict[int, str]:
    container = AppContainer()
    broker: BaseBroker = container.core.redis_broker.provided()

    api_key_repo: AbstractAPIKeyRepository = container.infrastructure.api_key_repo()
    result_repo: AbstractResultRepository = container.infrastructure.result_repo()

    api_keys = await api_key_repo.load_keys_from_db(keys_type=APIKeySourceType.VIRUS_TOTAL)

    total_requests = 0
    key_limits = {}
    for key in api_keys:
        max_requests_per_hour = SECONDS_IN_HOUR // VT_DELAY
        available_requests = min(max_requests_per_hour, key.limit)
        total_requests += available_requests
        key_limits[key.api_key] = available_requests

    messages = await broker.read_messages(queue_name=queue, count=total_requests)

    links = _prepare_messages(messages=messages)

    # => Распределяем сообщения по ключам, добавляя их в список APIKeyEntity.links_to_process
    _distribute_links_among_keys(api_keys, links, key_limits)

    vt_message_checker: AbstractMessageChecker = container.infrastructure.vt_message_checker(
        api_keys_entity=api_keys,
        queue=queue,
    )

    results = await vt_message_checker.process_batch()

    links_to_update = [
        ResultEntity(
            link_id=int(key),
            virus_total=value,
        ) for key, value in results.items()
    ]

    await result_repo.create_or_update_virus_total(results=links_to_update)

    return results


async def ae_validate_async(queue: str) -> dict[int, str]:
    container = AppContainer()
    broker: BaseBroker = container.core.redis_broker.provided()

    api_key_repo: AbstractAPIKeyRepository = container.infrastructure.api_key_repo()

    result_repo: AbstractResultRepository = container.infrastructure.result_repo()

    api_keys = await api_key_repo.load_keys_from_db(keys_type=APIKeySourceType.ABUSIVE_EXPERIENCE)

    total_requests = 0
    key_limits = {}
    for key in api_keys:
        total_requests += key.limit
        key_limits[key.api_key] = key.limit

    messages = await broker.read_messages(queue_name=queue, count=total_requests)

    links = _prepare_messages(messages=messages)

    # => Распределяем сообщения по ключам, добавляя их в список APIKeyEntity.links_to_process
    _distribute_links_among_keys(api_keys, links, key_limits)

    ae_message_checker: AbstractMessageChecker = container.infrastructure.ae_message_checker(
        api_keys_entity=api_keys,
        queue=queue,
    )

    results = await ae_message_checker.process_batch()

    links_to_update = [
        ResultEntity(
            link_id=int(key),
            abusive_experience=value,
        ) for key, value in results.items()
    ]

    await result_repo.create_or_update_abusive_experience(results=links_to_update)

    return results


async def reset_keys_limit_async() -> None:
    container = AppContainer()
    api_key_repo: AbstractAPIKeyRepository = container.infrastructure.api_key_repo()
    await api_key_repo.reset_daily_limits()
