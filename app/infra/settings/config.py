from infra.settings.stage.app import AppSettings
from infra.settings.stage.base import (
    AppEnvTypes,
    BaseAppSettings,
)
from infra.settings.stage.dev import DevAppSettings
from infra.settings.stage.prod import ProdAppSettings


environments: dict[AppEnvTypes, type[AppSettings]] = {
    AppEnvTypes.DEV: DevAppSettings,
    AppEnvTypes.PROD: ProdAppSettings,
}


def get_app_settings() -> AppSettings:
    settings = BaseAppSettings()
    app_env = settings.APP_ENV
    config = environments[app_env]
    return config()