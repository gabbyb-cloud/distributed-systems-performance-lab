import json

import redis
from redis.backoff import NoBackoff
from redis.exceptions import RedisError
from redis.retry import Retry

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
    socket_connect_timeout=0.1,
    socket_timeout=0.1,
    retry=Retry(NoBackoff(), 0),
)


def get_cached_item(item_id: int):
    try:
        value = redis_client.get(f"item:{item_id}")
    except RedisError:
        return None

    if value is None:
        return None

    return json.loads(value)


def cache_item(item):
    try:
        redis_client.set(
            f"item:{item['item_id']}",
            json.dumps(item),
            ex=60,
        )
    except RedisError:
        pass
    
