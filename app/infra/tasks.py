import asyncio

from infra.broker.base import BaseConsumer
from infra.celery_worker import app
from infra.ioc.container.application import AppContainer
from logic.message_processor.base import IMessageProcessor


@app.task
def vt_validate(topic: str = 'links', batch_size: int = 1, max_attempts: int = 5) -> dict[int, bool]:
    container = AppContainer()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def main():
        kafka_consumer: BaseConsumer = container.core.kafka_consumer()
        messages = await kafka_consumer.start_consuming(
            topic,
            batch_size,
            max_attempts,
        )
        vt_processor: IMessageProcessor = container.infrastructure.vt_message_processor()
        results = await vt_processor.process_batch(
            api_key=container.core.settings().VT_API_KEY,
            messages=messages,
        )
        return results

    results_dict = loop.run_until_complete(main())

    return results_dict
