import asyncio

from ..adapters.orm.credentials.abusive_experience_keys import AbusiveExperienceKeyModel
from ..adapters.orm.credentials.virus_total_keys import VirusTotalKeyModel
from ..adapters.repositories.api_keys_repository import AbstractAPIKeyRepository
from ..adapters.repositories.proxy_repository import AbstractProxyRepository
from ..adapters.repositories.result_repository import AbstractResultRepository
from ..domain.entities.result_entity import ResultEntity
from ..logic.message_processors.base import AbstractMessageChecker
from .broker.base import BaseBroker
from .celery_worker import app as celery_app
from .ioc.container.application import AppContainer


@celery_app.task
def vt_validate(queue: str = 'virus_total', batch_size: int = 1) -> dict[int, bool | None]:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(vt_validate_async(queue, batch_size))


@celery_app.task
def ae_validate(queue: str = 'abusive_exp', batch_size: int = 1) -> dict[int, bool | None]:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(ae_validate_async(queue, batch_size))


async def vt_validate_async(queue: str, batch_size: int) -> dict[int, bool | None]:
    container = AppContainer()
    broker: BaseBroker = container.core.redis_broker.provided()

    api_key_repo: AbstractAPIKeyRepository = container.infrastructure.api_key_repo(model=VirusTotalKeyModel)
    result_repo: AbstractResultRepository = container.infrastructure.result_repo()

    vt_message_checker: AbstractMessageChecker = container.infrastructure.vt_message_checker(
        api_key_repo=api_key_repo,
    )

    proxy_repo: AbstractProxyRepository = container.infrastructure.proxy_repo()
    if active_proxy := (await proxy_repo.get()):
        proxy_url = active_proxy.url
    else:
        proxy_url = None

    messages = await broker.read_messages(queue_name=queue, count=batch_size)

    results = await vt_message_checker.process_batch(messages, proxy=proxy_url)

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

    api_key_repo: AbstractAPIKeyRepository = container.infrastructure.api_key_repo(model=AbusiveExperienceKeyModel)

    result_repo: AbstractResultRepository = container.infrastructure.result_repo()

    ae_message_checker: AbstractMessageChecker = container.infrastructure.ae_message_checker(
        api_key_repo=api_key_repo,
    )

    proxy_repo: AbstractProxyRepository = container.infrastructure.proxy_repo()
    if active_proxy := (await proxy_repo.get()):
        proxy_url = active_proxy.url
    else:
        proxy_url = None

    messages = await broker.read_messages(queue_name=queue, count=batch_size)

    results = await ae_message_checker.process_batch(messages, proxy=proxy_url)

    links_to_update = [
        ResultEntity(
            link_id=int(key),
            abusive_experience=value,
        ) for key, value in results.items()
    ]

    await result_repo.create_or_update_abusive_experience(results=links_to_update)

    return results
