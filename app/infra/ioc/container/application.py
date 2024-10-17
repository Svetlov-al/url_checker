from app import (
    entrypoints,
    schemas,
)
from app.infra.ioc.container.core import CoreContainer
from app.infra.ioc.container.infrastructure import InfrastructureContainer
from app.infra.ioc.container.service import ServicesContainer
from dependency_injector import (
    containers,
    providers,
)


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
