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
from dtos.create_links_dto import CreateLinksDTO
from schemas.base import ErrorSchema
from schemas.create_links_request_schema import CreateUrlRequestSchema
from schemas.create_links_response_schema import CreateLinksResponseSchema

from domain.exceptions.base import ApplicationException
from infra.ioc.container.application import AppContainer
from logic.service_layer.create_links_service import CreateLinksService


router = APIRouter(tags=["URL's"])


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    description='Эндпоинт сохраняет список ссылок на проверку в базу данных',
    responses={
        status.HTTP_201_CREATED: {'model': CreateLinksResponseSchema},
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
    },
)
@inject
async def create_urls(
    schema: CreateUrlRequestSchema,
    service: CreateLinksService = Depends(Provide[AppContainer.services.create_links_service]),
) -> CreateLinksResponseSchema:
    """Сохранить ссылки."""
    params = CreateLinksDTO(links=schema.links)
    try:
        result = await service.run(params)
    except ApplicationException as exc:
        raise HTTPException(status_code=400, detail={'error': exc.message})

    return CreateLinksResponseSchema(
        message=f"Сохранено: {result} ссылок!",
        count=result,
    )
