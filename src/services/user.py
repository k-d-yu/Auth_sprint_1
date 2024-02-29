import datetime
import uuid

from jose import jwt
from jose.exceptions import ExpiredSignatureError

from core.config import jwt_settings
from db.redis_db import connect_redis

prefix_refresh_token = ' refresh_token'


async def create_access_token(data: dict) -> str:
    redis = await connect_redis()
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=jwt_settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, jwt_settings.jwt_secret_key, algorithm=jwt_settings.jwt_algorithm)
    await redis.sadd(*data.values(), encoded_jwt)
    redis.close()
    await redis.wait_closed()
    return encoded_jwt


async def create_refresh_token(user_id: str) -> str:
    refresh_token = str(uuid.uuid4())
    redis = await connect_redis()
    await redis.sadd(user_id + prefix_refresh_token, refresh_token)
    await redis.expire(user_id + prefix_refresh_token, jwt_settings.refresh_token_expire_days * 24 * 60 * 60)
    redis.close()
    await redis.wait_closed()
    return refresh_token


async def get_existing_refresh_token(user_id: str) -> str:
    redis = await connect_redis()
    existing_refresh_token = await redis.smembers(user_id + prefix_refresh_token)
    redis.close()
    await redis.wait_closed()
    return existing_refresh_token[0] if existing_refresh_token else None


async def get_existing_access_token(user_id: str) -> str:
    redis = await connect_redis()
    existing_access_token = await redis.smembers(user_id)
    try:
        if existing_access_token:
            decoded_token = jwt.decode(existing_access_token[0], jwt_settings.jwt_secret_key,
                                       algorithms=[jwt_settings.jwt_algorithm])
            redis.close()
            await redis.wait_closed()
            return existing_access_token[0]
        else:
            return None
    except ExpiredSignatureError:
        await redis.srem(user_id, existing_access_token[0])


async def get_refresh_token_from_id(user_id: str) -> str:
    redis = await connect_redis()
    refresh_token = await redis.smembers(user_id + prefix_refresh_token)
    redis.close()
    await redis.wait_closed()
    return refresh_token[0] if refresh_token else None


async def del_access_token(user_id: str):
    redis = await connect_redis()
    tokens = await redis.smembers(user_id)
    for token in tokens:
        await redis.delete(token)
    await redis.delete(user_id)
    redis.close()
    await redis.wait_closed()


async def del_refresh_token(user_id: str):
    redis = await connect_redis()
    tokens = await redis.smembers(user_id + prefix_refresh_token)
    for token in tokens:
        await redis.delete(token)
    await redis.delete(user_id + prefix_refresh_token)
    redis.close()
    await redis.wait_closed()
