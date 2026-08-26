import json

from redis.exceptions import RedisError

import app.cache as cache_module


def test_cache_hit(monkeypatch):
    cached_value = json.dumps(
        {
            "item_id": 1,
            "name": "item-1",
        }
    )

    monkeypatch.setattr(
        cache_module.redis_client,
        "get",
        lambda key: cached_value,
    )

    result = cache_module.get_cached_item(1)

    assert result == {
        "item_id": 1,
        "name": "item-1",
    }


def test_cache_miss(monkeypatch):
    monkeypatch.setattr(
        cache_module.redis_client,
        "get",
        lambda key: None,
    )

    result = cache_module.get_cached_item(1)

    assert result is None


def test_redis_failure_returns_none(monkeypatch):
    def redis_failure(key):
        raise RedisError("Redis unavailable")

    monkeypatch.setattr(
        cache_module.redis_client,
        "get",
        redis_failure,
    )

    result = cache_module.get_cached_item(1)

    assert result is None


def test_cache_write_survives_redis_failure(monkeypatch):
    def redis_failure(*args, **kwargs):
        raise RedisError("Redis unavailable")

    monkeypatch.setattr(
        cache_module.redis_client,
        "set",
        redis_failure,
    )

    cache_module.cache_item(
        {
            "item_id": 1,
            "name": "item-1",
        }
    )
    