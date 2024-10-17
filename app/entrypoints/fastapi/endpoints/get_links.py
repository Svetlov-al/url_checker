from fastapi import (
    Depends,
    status,
)
from fastapi.routing import APIRouter

from app.entrypoints.fastapi.filters.get_all_links_fitler import GetAllLinksFilters
from app.infra.ioc.container.application import AppContainer
from app.logic.service_layer.get_links_serivce import GetLinksService
from app.schemas.link_detail_schema import LinkDetailSchema
from app.schemas.link_list_response_schema import LinksResponseSchema
from dependency_injector.wiring import (
    inject,
    Provide,
)


router = APIRouter(tags=["URL's"])


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
    description='Эндпоинт отображает список ссылок.',
    responses={
        status.HTTP_200_OK: {'model': LinksResponseSchema},
    },
)
@inject
async def get_links(
    filters: GetAllLinksFilters = Depends(),
    service: GetLinksService = Depends(Provide[AppContainer.services.get_links_service]),
) -> LinksResponseSchema:
    """Отдает список ссылок."""
    results, count = await service.run(filters=filters.to_infra())

    return LinksResponseSchema(
        count=count,
        limit=filters.limit,
        offset=filters.offset,
        items=[LinkDetailSchema.from_entity(link) for link in results],
    )
