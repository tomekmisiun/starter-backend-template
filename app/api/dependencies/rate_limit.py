import hashlib

from fastapi import HTTPException, Request

from app.core.config import settings
from app.core.redis import redis_client


def rate_limit(
    limit: int | None = None,
    window_seconds: int | None = None,
    *,
    key_prefix: str = "rate_limit",
):
    if limit is not None and limit <= 0:
        raise ValueError("rate limit must be greater than 0")

    if window_seconds is not None and window_seconds <= 0:
        raise ValueError("rate limit window_seconds must be greater than 0")

    def dependency(request: Request):
        effective_limit = (
            limit if limit is not None else settings.rate_limit_default_limit
        )
        effective_window_seconds = (
            window_seconds
            if window_seconds is not None
            else settings.rate_limit_default_window_seconds
        )
        client_ip = request.client.host
        key = f"{key_prefix}:{client_ip}"

        current_count = redis_client.incr(key)

        if current_count == 1:
            redis_client.expire(key, effective_window_seconds)

        if current_count > effective_limit:
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
            )

    return dependency


def auth_login_rate_limit():
    return rate_limit(
        limit=settings.auth_login_rate_limit_limit,
        window_seconds=settings.auth_login_rate_limit_window_seconds,
        key_prefix="rate_limit:auth_login",
    )


def auth_register_rate_limit():
    return rate_limit(
        limit=settings.auth_register_rate_limit_limit,
        window_seconds=settings.auth_register_rate_limit_window_seconds,
        key_prefix="rate_limit:auth_register",
    )


def password_reset_rate_limit(request: Request):
    client_ip = request.client.host
    body = request.scope.get("_json")

    if isinstance(body, dict):
        email = str(body.get("email", "")).lower()
    else:
        email = ""

    email_hash = hashlib.sha256(email.encode("utf-8")).hexdigest()
    key = f"rate_limit:password_reset:{client_ip}:{email_hash}"
    current_count = redis_client.incr(key)

    if current_count == 1:
        redis_client.expire(
            key,
            settings.password_reset_rate_limit_window_seconds,
        )

    if current_count > settings.password_reset_rate_limit_limit:
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
        )
