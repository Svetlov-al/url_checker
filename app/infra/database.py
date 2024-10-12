import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncAttrs,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


logger = logging.getLogger(__name__)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Database:

    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(db_url, echo=True)
        self.async_session = async_sessionmaker(self._engine, expire_on_commit=False)

    async def create_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def session(self) -> AsyncSession:
        async_session: AsyncSession = self.async_session()
        try:
            yield async_session
        except Exception:
            await async_session.rollback()
            raise
        finally:
            await async_session.close()
