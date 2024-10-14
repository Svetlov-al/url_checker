import entrypoints
import schemas
from dependency_injector import (
    containers,
    providers,
)

from infra.ioc.container.core import CoreContainer
from infra.ioc.container.infrastructure import InfrastructureContainer
from infra.ioc.container.service import ServicesContainer


class AppContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        auto_wire=True,
        packages=[
            entrypoints,
            schemas,
        ],
    )

    core: CoreContainer = providers.Container(CoreContainer)
    infrastructure: InfrastructureContainer = providers.Container(InfrastructureContainer)
    services: ServicesContainer = providers.Container(ServicesContainer)
