from app.adapters.repositories.abusive_experience_repository import (
    AbstractAbusiveExperienceRepository,
    AbusiveExperienceRepository,
)
from app.adapters.repositories.link_repository import (
    AbstractLinkRepository,
    LinkRepository,
)
from app.adapters.repositories.virus_total_repository import (
    AbstractVirusTotalRepository,
    VirusTotalRepository,
)
from app.infra.ioc.container.core import CoreContainer
from app.logic.message_processors.abusive_experience_checker import AbusiveExperienceChecker
from app.logic.message_processors.base import IMessageProcessor
from app.logic.message_processors.virus_total_checker import VirusTotalChecker
from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import (
    Container,
    Factory,
)


class InfrastructureContainer(containers.DeclarativeContainer):
    core: Container[CoreContainer] = providers.Container(CoreContainer)

    link_repo: Factory[AbstractLinkRepository] = providers.Factory(
        LinkRepository,
        session_factory=core.db.provided.session,
    )
    vt_repo: Factory[AbstractVirusTotalRepository] = providers.Factory(
        VirusTotalRepository,
        session_factory=core.db.provided.session,
    )

    ae_repo: Factory[AbstractAbusiveExperienceRepository] = providers.Factory(
        AbusiveExperienceRepository,
        session_factory=core.db.provided.session,
    )

    vt_message_processor: Factory[IMessageProcessor] = providers.Factory(
        VirusTotalChecker,
    )

    ae_message_processor: Factory[IMessageProcessor] = providers.Factory(
        AbusiveExperienceChecker,
    )
