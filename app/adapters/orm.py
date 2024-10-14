from datetime import datetime

from sqlalchemy import (
    Boolean,
    func,
    Integer,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from infra.database import Base


class LinkModel(Base):
    __tablename__ = "link"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # noqa: A003
    url: Mapped[str] = mapped_column(String, nullable=False)
    virus_total: Mapped[bool] = mapped_column(Boolean, default=None, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    def __repr__(self):
        return (f"<LinkModel(id={self.id}, url='{self.url}', virus_total={self.virus_total}, "
                f"created_at={self.created_at}, updated_at={self.updated_at})>")
