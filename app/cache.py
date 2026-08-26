import json

import redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)


def get_cached_item(item_id: int):
    value = redis_client.get(f"item:{item_id}")

    if value is None:
        return None

    return json.loads(value)


def cache_item(item):
    redis_client.set(
        f"item:{item['item_id']}",
        json.dumps(item),
        ex=60,
    )
    