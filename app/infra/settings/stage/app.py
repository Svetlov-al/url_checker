from typing import Any

from pydantic import Field

from infra.settings.stage.base import BaseAppSettings


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
    POSTGRES_SCHEMA: str = Field(..., validation_alias="POSTGRES_SCHEMA")
    POSTGRES_URI: str = Field(..., validation_alias="POSTGRES_URI")

    MAX_CONNECTION: int = 10

    ALLOWED_HOSTS: list[str] = [
        "*",
    ]

    LOGGING_LEVEL: int = Field(20, validation_alias="LOGGING_LEVEL")
    FASTAPI_LOGGING_LEVEL: int = Field(50, validation_alias="FASTAPI_LOGGING_LEVEL")

    # BROKER
    KAFKA_URL: str = Field(..., validation_alias="KAFKA_URL")

    VT_API_KEY: str = Field(..., validation_alias="VT_API_KEY")

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
