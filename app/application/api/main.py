from contextlib import asynccontextmanager

from fastapi import FastAPI

from entrypoints.fastapi.endpoints.create_links import router as create_links_router
from entrypoints.fastapi.endpoints.get_good_links import router as get_good_links_router
from entrypoints.fastapi.endpoints.get_link_by_title import router as get_link_by_title_router

from infra.ioc.container.application import AppContainer
from infra.settings.stage.app import AppSettings


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = app.container.core.container.db.provided() # noqa
    await db.create_database()
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
    app.include_router(get_good_links_router, prefix='/urls')
    app.include_router(get_link_by_title_router, prefix='/urls')

    return app
