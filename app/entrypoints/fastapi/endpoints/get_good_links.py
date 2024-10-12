from fastapi import (
    Depends,
    status,
)
from fastapi.routing import APIRouter

from dependency_injector.wiring import (
    inject,
    Provide,
)
from entrypoints.fastapi.filters.get_all_links_fitler import GetAllLinksFilters
from schemas.base import ErrorSchema
from schemas.link_detail_schema import LinkDetailSchema
from schemas.link_list_response_schema import LinksResponseSchema

from infra.ioc.container.application import AppContainer
from logic.service_layer.get_good_links_serivce import GetGoodLinksService


router = APIRouter(tags=["URL's"])


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
    description='Эндпоинт отображает список ссылок.',
    responses={
        status.HTTP_200_OK: {'model': LinksResponseSchema},
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
    },
)
@inject
async def get_good_urls(
    filters: GetAllLinksFilters = Depends(),
    service: GetGoodLinksService = Depends(Provide[AppContainer.services.get_good_links_service]),
) -> LinksResponseSchema:
    """Отдает список ссылок."""
    result, count = await service.run(filters=filters.to_infra())

    return LinksResponseSchema(
        count=count,
        limit=filters.limit,
        offset=filters.offset,
        items=[LinkDetailSchema.from_entity(link) for link in result],
    )
