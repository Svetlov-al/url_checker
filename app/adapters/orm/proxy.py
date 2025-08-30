from typing import Optional

from app.adapters.orm.mixins.timestamp import TimestampMixin
from app.database.settings.base import Base
from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.sql.sqltypes import BigInteger


class ProxyModel(Base, TimestampMixin):
    __tablename__ = "proxy"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)  # noqa: A003
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    api_keys: Mapped[list["APIKeyModel"]] = relationship(  # noqa
        "APIKeyModel",
        secondary="proxy_keys",
        back_populates="proxies",
        lazy='select',
    )

    def __repr__(self):
        return f"<ProxyModel(id={self.id}, url={self.url}, is_active={self.is_active})>"


class ProxyKeysAssociation(Base):
    __tablename__ = 'proxy_keys'

    proxy_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("proxy.id", ondelete="CASCADE"),
        primary_key=True,
    )
    key_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("api_credential.id", ondelete="CASCADE"),
        primary_key=True,
    )
    extra_data: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
