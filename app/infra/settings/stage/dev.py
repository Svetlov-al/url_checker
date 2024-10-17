from app.infra.settings.stage.app import AppSettings


class DevAppSettings(AppSettings):
    DEBUG: bool = True
