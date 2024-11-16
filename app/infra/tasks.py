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
from .broker.base import BaseBroker
from .celery_worker import app as celery_app
from .ioc.container.application import AppContainer


@celery_app.task
def vt_validate(queue: str = 'virus_total') -> dict[int, str]:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(vt_validate_async(queue))


@celery_app.task
def ae_validate(queue: str = 'abusive_exp') -> dict[int, bool | None]:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(ae_validate_async(queue))


async def vt_validate_async(queue: str) -> dict[int, str]:
    container = AppContainer()
    broker: BaseBroker = container.core.redis_broker.provided()

    api_key_repo: AbstractAPIKeyRepository = container.infrastructure.api_key_repo()
    result_repo: AbstractResultRepository = container.infrastructure.result_repo()

    api_keys = await api_key_repo.load_keys_from_db(keys_type=APIKeySourceType.VIRUS_TOTAL)
    vt_message_checker: AbstractMessageChecker = container.infrastructure.vt_message_checker(
        api_keys_entity=api_keys,
    )

    total_requests = 0
    for key in api_keys:
        max_requests_per_hour = SECONDS_IN_HOUR // VT_DELAY
        available_requests = min(max_requests_per_hour, key.limit)
        total_requests += available_requests

    messages = await broker.read_messages(queue_name=queue, count=total_requests)

    results = await vt_message_checker.process_batch(messages)

    links_to_update = [
        ResultEntity(
            link_id=int(key),
            virus_total=value,
        ) for key, value in results.items()
    ]

    await result_repo.create_or_update_virus_total(results=links_to_update)

    return results


async def ae_validate_async(queue: str, batch_size: int) -> dict[int, bool | None]:
    container = AppContainer()
    broker: BaseBroker = container.core.redis_broker.provided()

    api_key_repo: AbstractAPIKeyRepository = container.infrastructure.api_key_repo()

    result_repo: AbstractResultRepository = container.infrastructure.result_repo()

    ae_message_checker: AbstractMessageChecker = container.infrastructure.ae_message_checker(
        api_key_repo=api_key_repo,
    )

    messages = await broker.read_messages(queue_name=queue, count=batch_size)

    results = await ae_message_checker.process_batch(messages)

    links_to_update = [
        ResultEntity(
            link_id=int(key),
            abusive_experience=value,
        ) for key, value in results.items()
    ]

    await result_repo.create_or_update_abusive_experience(results=links_to_update)

    return results
