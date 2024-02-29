import time

from redis import Redis
from redis.exceptions import ConnectionError
from tests.functional.settings import settings

if __name__ == '__main__':
    redis_client = Redis(host=settings.redis_host, port=settings.redis_port)
    while True:
        try:
            redis_client.ping()
            break
        except ConnectionError:
            time.sleep(1)

