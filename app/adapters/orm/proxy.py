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


class ProxyModel(Base, TimestampMixin):
    __tablename__ = "proxies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # noqa: A003
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self):
        return f"<ProxyModel(id={self.id}, url={self.url}, is_active={self.is_active})>"
