from app.infra.ioc.container.core import CoreContainer
from app.infra.ioc.container.infrastructure import InfrastructureContainer
from app.logic.service_layer.create_links_service import CreateLinksService
from app.logic.service_layer.get_link_by_title_service import GetLinksByDomainListService
from app.logic.service_layer.get_links_serivce import GetLinksService
from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Factory


class ServicesContainer(containers.DeclarativeContainer):

    core: CoreContainer = providers.Container(CoreContainer)
    infrastructure: InfrastructureContainer = providers.Container(InfrastructureContainer)

    create_links_service: Factory[CreateLinksService] = providers.Factory(
        CreateLinksService,
        repo=infrastructure.link_repo.provided,
    )

    get_links_service: Factory[GetLinksService] = providers.Factory(
        GetLinksService,
        repo=infrastructure.link_repo.provided,
    )

    get_links_by_domain_list_service: Factory[GetLinksByDomainListService] = providers.Factory(
        GetLinksByDomainListService,
        repo=infrastructure.link_repo.provided,
    )
