from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.routing import APIRouter

from dependency_injector.wiring import (
    inject,
    Provide,
)
from dtos.get_link_dto import GetLinkDTO
from schemas.base import ErrorSchema
from schemas.get_link_request_schema import GetLinkRequestSchema
from schemas.link_detail_schema import LinkDetailSchema

from domain.exceptions.link_not_found_exception import LinkNotFoundException
from infra.ioc.container.application import AppContainer
from logic.service_layer.get_link_by_title_service import GetLinkByTitleService


router = APIRouter(tags=["URL's"])


@router.post(
    '/by_title/',
    status_code=status.HTTP_200_OK,
    description='Эндпоинт отображает ссылку по наименованию',
    responses={
        status.HTTP_200_OK: {'model': LinkDetailSchema},
        status.HTTP_404_NOT_FOUND: {'model': ErrorSchema},
    },
)
@inject
async def get_url_by_title(
    title: GetLinkRequestSchema,
    service: GetLinkByTitleService = Depends(Provide[AppContainer.services.get_link_by_title_service]),
) -> LinkDetailSchema:
    """Отдает информацию по ссылке."""
    params = GetLinkDTO(
        url=title.url,
    )
    try:
        result = await service.run(params)
    except LinkNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'error': exc.message})

    return LinkDetailSchema.from_entity(result)
