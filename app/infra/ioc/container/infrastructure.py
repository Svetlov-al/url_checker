from app.adapters.repositories.api_keys_repository import (
    AbstractAPIKeyRepository,
    APIKeyRepository,
)
from app.adapters.repositories.link_repository import (
    AbstractLinkRepository,
    LinkRepository,
)
from app.adapters.repositories.proxy_repository import (
    AbstractProxyRepository,
    ProxyRepository,
)
from app.adapters.repositories.result_repository import (
    AbstractResultRepository,
    ResultRepository,
)
from app.infra.ioc.container.core import CoreContainer
from app.logic.message_processors.abusive_experience_checker import AbusiveExperienceChecker
from app.logic.message_processors.base import AbstractMessageChecker
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

    result_repo: Factory[AbstractResultRepository] = providers.Factory(
        ResultRepository,
        session_factory=core.db.provided.session,
    )

    api_key_repo: Factory[AbstractAPIKeyRepository] = providers.Factory(
        APIKeyRepository,
        session_factory=core.db.provided.session,
    )

    proxy_repo: Factory[AbstractProxyRepository] = providers.Factory(
        ProxyRepository,
        session_factory=core.db.provided.session,
    )

    vt_message_checker: Factory[AbstractMessageChecker] = providers.Factory(
        VirusTotalChecker,
    )

    ae_message_checker: Factory[AbstractMessageChecker] = providers.Factory(
        AbusiveExperienceChecker,
    )
