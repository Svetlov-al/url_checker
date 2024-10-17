from app.adapters.orm.mixins.timestamp import TimestampMixin
from app.database.settings.base import Base
from sqlalchemy import (
    Boolean,
    Integer,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)


class VirusTotalKeyModel(Base, TimestampMixin):
    __tablename__ = "virus_total_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # noqa: A003
    api_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __str__(self) -> str:
        return f"ID: {self.id}, Token: {self.api_key}, Valid: {self.is_valid}"
