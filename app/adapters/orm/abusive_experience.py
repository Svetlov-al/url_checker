from app.adapters.orm.mixins.timestamp import TimestampMixin
from app.database.settings.base import Base
from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class AbusiveExperienceModel(Base, TimestampMixin):
    __tablename__ = "abusive_experience"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # noqa: A003
    result: Mapped[bool] = mapped_column(Boolean, nullable=True)

    link_id: Mapped[int] = mapped_column(Integer, ForeignKey("link.id", ondelete="CASCADE"), unique=True)
    link: Mapped["LinkModel"] = relationship("LinkModel", back_populates="abusive_experience")  # noqa

    def __repr__(self) -> str:
        return (
            f"<AbusiveExperienceModel(id={self.id}, result={self.result}, link_id={self.link_id})>"
        )

    def __str__(self) -> str:
        return (
            f"LinkID: {self.id}, Result: {self.result}"
        )
