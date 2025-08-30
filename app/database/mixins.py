from sqlalchemy.ext.asyncio.session import AsyncSession


class QueryMixin:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
