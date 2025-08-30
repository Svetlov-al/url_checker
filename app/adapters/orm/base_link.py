from app.adapters.orm.mixins.timestamp import TimestampMixin
from app.database.settings.base import Base
from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.sql.sqltypes import BigInteger


class LinkModel(Base, TimestampMixin):
    __tablename__ = "link"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)  # noqa: A003
    url: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    result: Mapped["ResultModel"] = relationship(  # noqa
        "ResultModel", back_populates="link",
        uselist=False,
        lazy='joined',
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<LinkModel(id={self.id}, url='{self.url}',"
            f" created_at={self.created_at}, updated_at={self.updated_at})>"
        )

    def __str__(self) -> str:
        return (
            f"{self.url}"
        )
