from fastapi import HTTPException, Request

from app.core.redis import redis_client


def rate_limit(limit: int = 5, window_seconds: int = 60):
    def dependency(request: Request):
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"

        current_count = redis_client.incr(key)

        if current_count == 1:
            redis_client.expire(key, window_seconds)

        if current_count > limit:
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
            )

    return dependency