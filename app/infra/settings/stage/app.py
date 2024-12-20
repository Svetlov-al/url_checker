from typing import Any

from app.infra.settings.stage.base import BaseAppSettings
from pydantic import Field


class AppSettings(BaseAppSettings):
    """FASTAPI."""
    DEBUG: bool = Field(..., validation_alias="DEBUG")
    DOCS_URL: str | None = "/docs"
    OPENAPI_PREFIX: str = ""
    DESCRIPTION: str = ""
    OPENAPI_URL: str | None = None
    REDOC_URL: str | None = None
    TITLE: str = ""
    VERSION: str = "0.0.1"
    HOST: str = Field("0.0.0.0", validation_alias="HOST")
    PORT: int = Field(5005, validation_alias="PORT")
    RELOAD: bool = Field(True, validation_alias="RELOAD")
    """POSTGRES SETTINGS."""

    SQLALCHEMY_DATABASE_URL: str = Field(..., validation_alias="SQLALCHEMY_DATABASE_URL")

    MAX_CONNECTION: int = 10

    ALLOWED_HOSTS: list[str] = [
        "*",
    ]

    LOGGING_LEVEL: int = Field(20, validation_alias="LOGGING_LEVEL")
    FASTAPI_LOGGING_LEVEL: int = Field(50, validation_alias="FASTAPI_LOGGING_LEVEL")

    # BROKER
    REDIS_HOST: str = Field("localhost", validation_alias="REDIS_HOST")
    REDIS_PORT: int = Field(6379, validation_alias="REDIS_PORT")

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        return {
            "debug": self.DEBUG,
            "docs_url": self.DOCS_URL,
            "redoc_url": self.REDOC_URL,
            "title": self.TITLE,
            "version": self.VERSION,
            "description": self.DESCRIPTION,
            "swagger_ui_parameters": {"syntaxHighlight.theme": "obsidian"},
        }
