import json
import os

import redis
from dotenv import load_dotenv
from redis.backoff import NoBackoff
from redis.exceptions import RedisError
from redis.retry import Retry

from app.metrics import CACHE_ERRORS, CACHE_HITS, CACHE_MISSES

load_dotenv()

redis_client = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    decode_responses=True,
    socket_connect_timeout=0.1,
    socket_timeout=0.1,
    retry=Retry(NoBackoff(), 0),
)


def get_cached_item(item_id: int):
    try:
        value = redis_client.get(f"item:{item_id}")
    except RedisError:
        CACHE_ERRORS.inc()
        return None

    if value is None:
        CACHE_MISSES.inc()
        return None

    CACHE_HITS.inc()
    return json.loads(value)


def cache_item(item):
    try:
        redis_client.set(
            f"item:{item['item_id']}",
            json.dumps(item),
            ex=60,
        )
    except RedisError:
        CACHE_ERRORS.inc()
        

