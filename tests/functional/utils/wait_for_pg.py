import time

from sqlalchemy.ext.asyncio import create_async_engine
from tests.functional.settings import settings

if __name__ == '__main__':
    dsn = f'postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}'
    engine = create_async_engine(dsn, pool_size=20, max_overflow=0)

    while True:
        if engine.connect():
            break
        time.sleep(1)

