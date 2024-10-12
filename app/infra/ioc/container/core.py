from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Factory

from infra.database import Database
from infra.settings.config import get_app_settings
from infra.settings.stage.app import AppSettings


class CoreContainer(containers.DeclarativeContainer):
    settings: Factory[AppSettings] = providers.Callable(get_app_settings)
    db: Factory[Database] = providers.Singleton(Database, db_url=settings().POSTGRES_URI)
