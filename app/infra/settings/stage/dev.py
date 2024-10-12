from infra.settings.stage.app import AppSettings


class DevAppSettings(AppSettings):
    DEBUG: bool = True
