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
from logic.message_processor.base import IMessageProcessor
from logic.message_processor.virus_total_checker import VirusTotalChecker


class InfrastructureContainer(containers.DeclarativeContainer):
    core: Container[CoreContainer] = providers.Container(CoreContainer)

    link_repo: Factory[AbstractRepository] = providers.Factory(
        LinkRepository,
        session_factory=core.db.provided.session,
    )

    vt_message_processor: Factory[IMessageProcessor] = providers.Factory(
        VirusTotalChecker,
    )
