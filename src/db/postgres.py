from core.config import settings
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker

Base = declarative_base()

dsn = f'postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}'
engine: AsyncEngine = create_async_engine(dsn, echo=True, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def create_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
