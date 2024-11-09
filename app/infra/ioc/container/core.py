from app.database.settings.development import Database
from app.infra.broker.base import BaseBroker
from app.infra.broker.redis_broker import RedisMessageBroker
from app.infra.settings.config import get_app_settings
from app.infra.settings.redis_connection import init_redis_pool
from app.infra.settings.stage.app import AppSettings
from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Factory
from redis.asyncio import Redis


class CoreContainer(containers.DeclarativeContainer):
    settings: Factory[AppSettings] = providers.Callable(get_app_settings)
    db: Factory[Database] = providers.Singleton(Database, db_url=settings().SQLALCHEMY_DATABASE_URL)

    redis_pool: Factory[Redis] = providers.Resource(
        init_redis_pool,
        host=settings().REDIS_HOST,
        port=settings().REDIS_PORT,
    )
    redis_broker: providers.Factory[BaseBroker] = providers.Factory(
        RedisMessageBroker,
        redis=redis_pool,
    )
