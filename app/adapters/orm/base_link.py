from app.adapters.orm.mixins.timestamp import TimestampMixin
from app.database.settings.base import Base
from sqlalchemy import (
    Integer,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class LinkModel(Base, TimestampMixin):
    __tablename__ = "link"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # noqa: A003
    url: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    abusive_experience: Mapped["AbusiveExperienceModel"] = relationship(  # noqa
        "AbusiveExperienceModel", back_populates="link",
        uselist=False,
        lazy='joined',
    )
    virus_total: Mapped["VirusTotalModel"] = relationship(  # noqa
        "VirusTotalModel", back_populates="link",
        uselist=False,
        lazy='joined',
    )

    def __repr__(self) -> str:
        return (f"<LinkModel(id={self.id}, url='{self.url}',"
                f" created_at={self.created_at}, updated_at={self.updated_at})>")

    def __str__(self) -> str:
        return (
            f"{self.url}"
        )
