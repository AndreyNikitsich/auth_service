from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from settings import settings


class Base(DeclarativeBase):
    pass


dsn = (
    f"postgresql+asyncpg://{settings.pg.db_user}:{settings.pg.db_password}@"
    f"{settings.pg.db_host}:{settings.pg.db_port}/{settings.pg.db_name}"
)
engine = create_async_engine(dsn, echo=True, future=True)
async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def create_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def purge_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
