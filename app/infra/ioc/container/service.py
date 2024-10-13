from dependency_injector import (
    containers,
    providers,
)
from dependency_injector.providers import Factory

from infra.ioc.container.core import CoreContainer
from infra.ioc.container.infrastructure import InfrastructureContainer
from logic.service_layer.create_links_service import CreateLinksService
from logic.service_layer.get_good_links_serivce import GetGoodLinksService
from logic.service_layer.get_link_by_title_service import GetLinkByTitleService


class ServicesContainer(containers.DeclarativeContainer):

    core: CoreContainer = providers.Container(CoreContainer)
    infrastructure: InfrastructureContainer = providers.Container(InfrastructureContainer)

    create_links_service: Factory[CreateLinksService] = providers.Factory(
        CreateLinksService,
        repo=infrastructure.link_repo.provided,
        kafka_producer=core.kafka_producer.provided,
    )

    get_good_links_service: Factory[GetGoodLinksService] = providers.Factory(
        GetGoodLinksService,
        repo=infrastructure.link_repo.provided,
    )

    get_link_by_title_service: Factory[GetLinkByTitleService] = providers.Factory(
        GetLinkByTitleService,
        repo=infrastructure.link_repo.provided,
    )
