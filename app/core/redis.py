from datetime import datetime, timezone

from redis import Redis

from app.core.config import settings

redis_client = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True,
)


def revoke_refresh_token(jti: str, expires_at: int) -> None:
    ttl_seconds = expires_at - int(datetime.now(timezone.utc).timestamp())

    if ttl_seconds <= 0:
        return

    redis_client.set(
        f"revoked_refresh_token:{jti}",
        "1",
        ex=ttl_seconds,
    )


def is_refresh_token_revoked(jti: str) -> bool:
    return redis_client.exists(f"revoked_refresh_token:{jti}") == 1
