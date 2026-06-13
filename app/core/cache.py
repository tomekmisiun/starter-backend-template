import json
import logging

from redis import Redis
from redis.exceptions import RedisError

from app.core.redis import redis_client

logger = logging.getLogger("app.cache")


def get_json_cache(
    key: str,
    *,
    redis: Redis | None = None,
):
    client = redis if redis is not None else redis_client

    try:
        cached_value = client.get(key)
    except RedisError:
        logger.warning("cache_read_failed key=%s", key, exc_info=True)
        return None

    if cached_value is None:
        return None

    return json.loads(cached_value)


def set_json_cache(
    key: str,
    value,
    *,
    ttl_seconds: int,
    redis: Redis | None = None,
) -> None:
    client = redis if redis is not None else redis_client

    try:
        client.set(key, json.dumps(value), ex=ttl_seconds)
    except RedisError:
        logger.warning("cache_write_failed key=%s", key, exc_info=True)


def delete_cache_pattern(
    pattern: str,
    *,
    redis: Redis | None = None,
) -> int:
    client = redis if redis is not None else redis_client

    try:
        keys = list(client.scan_iter(match=pattern))
    except RedisError:
        logger.warning("cache_delete_scan_failed pattern=%s", pattern, exc_info=True)
        return 0

    if not keys:
        return 0

    try:
        return client.delete(*keys)
    except RedisError:
        logger.warning("cache_delete_failed pattern=%s", pattern, exc_info=True)
        return 0
