import asyncio

from ..adapters.orm.credentials.abusive_experience_keys import AbusiveExperienceKeyModel
from ..adapters.orm.credentials.virus_total_keys import VirusTotalKeyModel
from ..adapters.repositories.abusive_experience_repository import AbstractAbusiveExperienceRepository
from ..adapters.repositories.api_keys_repository import AbstractAPIKeyRepository
from ..adapters.repositories.virus_total_repository import AbstractVirusTotalRepository
from ..domain.entities.abusive_experience_entity import AbusiveExperienceEntity
from ..domain.entities.virus_total_entity import VirusTotalEntity
from ..logic.message_processors.base import IMessageProcessor
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
    vt_repo: AbstractVirusTotalRepository = container.infrastructure.vt_repo()

    vt_processor: IMessageProcessor = container.infrastructure.vt_message_processor(
        api_key_repo=api_key_repo,
    )

    messages = await broker.read_messages(queue_name=queue, count=batch_size)

    results = await vt_processor.process_batch(messages)

    links_to_update = [
        VirusTotalEntity(
            link_id=int(key),
            result=value,
        ) for key, value in results.items()
    ]

    await vt_repo.create_many(results=links_to_update)

    return results


async def ae_validate_async(queue: str, batch_size: int) -> dict[int, bool | None]:
    container = AppContainer()
    broker: BaseBroker = container.core.redis_broker.provided()

    api_key_repo: AbstractAPIKeyRepository = container.infrastructure.api_key_repo(model=AbusiveExperienceKeyModel)

    ae_repo: AbstractAbusiveExperienceRepository = container.infrastructure.ae_repo()

    ae_processor: IMessageProcessor = container.infrastructure.ae_message_processor(
        api_key_repo=api_key_repo,
    )

    messages = await broker.read_messages(queue_name=queue, count=batch_size)

    results = await ae_processor.process_batch(messages)

    links_to_update = [
        AbusiveExperienceEntity(
            link_id=int(key),
            result=value,
        ) for key, value in results.items()
    ]

    await ae_repo.create_many(results=links_to_update)

    return results
