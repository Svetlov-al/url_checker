from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Factory

from infra.broker.base import (
    BaseConsumer,
    BaseProducer,
)
from infra.database import Database
from infra.settings.config import get_app_settings
from infra.settings.kafka_broker import (
    create_message_consumer,
    create_message_producer,
)
from infra.settings.stage.app import AppSettings


class CoreContainer(containers.DeclarativeContainer):
    settings: Factory[AppSettings] = providers.Callable(get_app_settings)
    db: Factory[Database] = providers.Singleton(Database, db_url=settings().POSTGRES_URI)

    kafka_producer: providers.Factory[BaseProducer] = providers.Factory(
        create_message_producer,
        kafka_url=settings().KAFKA_URL,
    )

    kafka_consumer: Factory[BaseConsumer] = providers.Factory(
        create_message_consumer,
        kafka_url=settings().KAFKA_URL,
    )
