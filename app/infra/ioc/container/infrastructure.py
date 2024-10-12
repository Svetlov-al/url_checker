from adapters.repository import (
    AbstractRepository,
    LinkRepository,
)
from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import (
    Container,
    Factory,
)

from infra.ioc.container.core import CoreContainer


class InfrastructureContainer(containers.DeclarativeContainer):
    core: Container[CoreContainer] = providers.Container(CoreContainer)

    link_repo: Factory[AbstractRepository] = providers.Factory(
        LinkRepository,
        session_factory=core.db.provided.session,
    )
