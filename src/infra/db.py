from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession as AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from ..settings import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=settings.debug)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


async def close_db() -> None:
    await engine.dispose()
