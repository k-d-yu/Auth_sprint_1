import aioredis

from redis.asyncio import Redis

from core.config import settings

redis: Redis | None = None


async def get_redis() -> Redis:
    return redis


async def connect_redis():
    redis_url = f'redis://{settings.redis_host}:{settings.redis_port}'
    redis = await aioredis.create_redis_pool(redis_url)
    return redis
