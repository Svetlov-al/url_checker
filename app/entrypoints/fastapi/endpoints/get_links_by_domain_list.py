from fastapi import (
    Depends,
    status,
)
from fastapi.routing import APIRouter

from app.infra.ioc.container.application import AppContainer
from app.logic.service_layer.get_link_by_title_service import GetLinksByDomainListService
from app.schemas.get_link_request_schema import GetLinksRequestSchema
from app.schemas.link_detail_schema import LinkDetailSchema
from dependency_injector.wiring import (
    inject,
    Provide,
)


router = APIRouter(tags=["URL's"])


@router.post(
    '/by_domain/',
    status_code=status.HTTP_200_OK,
    description='Эндпоинт отображает ссылку по наименованию',
    responses={
        status.HTTP_200_OK: {'model': LinkDetailSchema},
    },
)
@inject
async def get_links_by_domain_list(
    domains: GetLinksRequestSchema,
    service: GetLinksByDomainListService = Depends(Provide(AppContainer.services.get_links_by_domain_list_service)),
) -> list[LinkDetailSchema]:
    """Отдает информацию по списку ссылок."""

    results = await service.run(domains.links)

    return [LinkDetailSchema.from_entity(result) for result in results]
