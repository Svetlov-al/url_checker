from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.application.admin_panel.admin.base_admin import create_admin
from app.database.settings.development import Database
from app.entrypoints.fastapi.endpoints.create_links import router as create_links_router
from app.entrypoints.fastapi.endpoints.get_links import router as get_links_router
from app.entrypoints.fastapi.endpoints.get_links_by_domain_list import router as get_links_by_domain_list_router
from app.infra.ioc.container.application import AppContainer
from app.infra.settings.stage.app import AppSettings


@asynccontextmanager
async def lifespan(app: FastAPI):
    db: Database = app.container.core.db.provided()  # noqa
    yield


def create_app() -> FastAPI:
    container = AppContainer()
    settings: AppSettings = container.core.settings()

    app = FastAPI(
        **settings.fastapi_kwargs,
        lifespan=lifespan,
    )

    app.container = container
    app.include_router(create_links_router, prefix='/urls')
    app.include_router(get_links_router, prefix='/urls')
    app.include_router(get_links_by_domain_list_router, prefix='/urls')

    create_admin(app)

    return app
