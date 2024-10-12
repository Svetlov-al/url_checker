from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Factory

from infra.broker.base import BaseMessageBroker
from infra.database import Database
from infra.settings.config import get_app_settings
from infra.settings.kafka_broker import create_message_broker
from infra.settings.stage.app import AppSettings


class CoreContainer(containers.DeclarativeContainer):
    settings: Factory[AppSettings] = providers.Callable(get_app_settings)
    db: Factory[Database] = providers.Singleton(Database, db_url=settings().POSTGRES_URI)
    kafka_broker: providers.Singleton[BaseMessageBroker] = providers.Singleton(
        create_message_broker,
        kafka_url=settings().KAFKA_URL,
    )
