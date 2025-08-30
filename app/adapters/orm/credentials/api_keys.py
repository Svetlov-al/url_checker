from enum import StrEnum

from app.adapters.orm.mixins.timestamp import TimestampMixin
from app.database.settings.base import Base
from sqlalchemy import (
    Boolean,
    Integer,
    String,
)
from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.sql.sqltypes import BigInteger


class APIKeySourceType(StrEnum):
    VIRUS_TOTAL = "virus_total"
    ABUSIVE_EXPERIENCE = "abusive_experience"


class APIKeyModel(Base, TimestampMixin):
    __tablename__ = "api_credential"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)  # noqa: A003
    api_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    daily_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=500)
    used_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source: Mapped[APIKeySourceType] = mapped_column(ENUM(APIKeySourceType), nullable=False)

    proxies: Mapped[list["ProxyModel"]] = relationship(  # noqa
        "ProxyModel",
        secondary="proxy_keys",
        back_populates="api_keys",
        lazy='select',
    )

    def __str__(self) -> str:
        return f"ID: {self.id}, Source: {self.source}, Token: {self.api_key}, Valid: {self.is_valid}"
