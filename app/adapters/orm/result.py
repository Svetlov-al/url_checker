from datetime import datetime
from enum import StrEnum

from app.adapters.orm.mixins.timestamp import TimestampMixin
from app.database.settings.base import Base
from sqlalchemy import (
    DateTime,
    event,
    ForeignKey,
    Integer,
)
from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class ResultStatus(StrEnum):
    GOOD = "good"
    FAIL = "fail"
    WAITING = "waiting"


class ResultModel(Base, TimestampMixin):
    __tablename__ = "result"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # noqa: A003

    virus_total: Mapped[ResultStatus] = mapped_column(
        ENUM(ResultStatus),
        nullable=False,
        default=ResultStatus.WAITING,
    )
    abusive_experience: Mapped[ResultStatus] = mapped_column(
        ENUM(ResultStatus),
        nullable=False,
        default=ResultStatus.WAITING,
    )

    link_id: Mapped[int] = mapped_column(Integer, ForeignKey("link.id", ondelete="CASCADE"), unique=True)
    link: Mapped["LinkModel"] = relationship("LinkModel", back_populates="result")  # noqa

    complete_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"<ResultModel(id={self.id}, link_id={self.link_id})>"
        )

    def __str__(self) -> str:
        return (
            f"LinkID: {self.id}"
        )


@event.listens_for(ResultModel, 'before_update')
def before_update_listener(mapper, connection, target):
    if target.virus_total != ResultStatus.WAITING and target.abusive_experience != ResultStatus.WAITING:
        if target.virus_total is not None and target.abusive_experience is not None:
            if target.complete_date is None:
                target.complete_date = datetime.now()
