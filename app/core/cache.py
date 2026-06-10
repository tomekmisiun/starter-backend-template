import json

from redis import Redis

from app.core.redis import redis_client


def get_json_cache(
    key: str,
    *,
    redis: Redis = redis_client,
):
    cached_value = redis.get(key)

    if cached_value is None:
        return None

    return json.loads(cached_value)


def set_json_cache(
    key: str,
    value,
    *,
    ttl_seconds: int,
    redis: Redis = redis_client,
) -> None:
    redis.set(key, json.dumps(value), ex=ttl_seconds)


def delete_cache_pattern(
    pattern: str,
    *,
    redis: Redis = redis_client,
) -> int:
    keys = list(redis.scan_iter(match=pattern))

    if not keys:
        return 0

    return redis.delete(*keys)
