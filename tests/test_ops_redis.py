from uuid import uuid4

import pytest

from app.core.cache import get_json_cache, set_json_cache
from tests.test_users import auth_headers, create_user_and_login, make_admin


def test_admin_list_users_propagates_cache_read_failures(
    db,
    client,
    monkeypatch,
):
    email = f"redis-read-fail-{uuid4().hex}@example.com"
    token, _ = create_user_and_login(db, client, email)
    make_admin(db, email)

    def failing_get_json_cache(*args, **kwargs):
        raise ConnectionError("redis unavailable")

    monkeypatch.setattr(
        "app.services.user_service.get_json_cache",
        failing_get_json_cache,
    )

    with pytest.raises(ConnectionError, match="redis unavailable"):
        client.get("/users/", headers=auth_headers(token))


def test_admin_list_users_propagates_cache_write_failures(
    db,
    client,
    monkeypatch,
):
    email = f"redis-write-fail-{uuid4().hex}@example.com"
    token, _ = create_user_and_login(db, client, email)
    make_admin(db, email)

    def failing_set_json_cache(*args, **kwargs):
        raise ConnectionError("redis unavailable")

    monkeypatch.setattr(
        "app.services.user_service.set_json_cache",
        failing_set_json_cache,
    )

    with pytest.raises(ConnectionError, match="redis unavailable"):
        client.get("/users/", headers=auth_headers(token))


def test_users_list_cache_misses_return_consistent_results(db, client, monkeypatch):
    email = f"cache-stampede-{uuid4().hex}@example.com"
    token, _ = create_user_and_login(db, client, email)
    make_admin(db, email)
    headers = auth_headers(token)

    monkeypatch.setattr(
        "app.services.user_service.get_json_cache",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.user_service.set_json_cache",
        lambda *args, **kwargs: None,
    )

    first_response = client.get("/users/", headers=headers)
    second_response = client.get("/users/", headers=headers)

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json() == second_response.json()


def test_limited_endpoint_returns_server_error_when_redis_is_unavailable(
    client,
    monkeypatch,
):
    class UnavailableRedis:
        def incr(self, *args, **kwargs):
            raise ConnectionError("redis unavailable")

        def expire(self, *args, **kwargs):
            raise ConnectionError("redis unavailable")

    monkeypatch.setattr(
        "app.api.dependencies.rate_limit.redis_client",
        UnavailableRedis(),
    )

    with pytest.raises(ConnectionError):
        client.get("/health/limited")


def test_json_cache_helpers_require_working_redis():
    cache_key = f"ops-redis-smoke:{uuid4().hex}"

    set_json_cache(cache_key, {"ok": True}, ttl_seconds=30)

    assert get_json_cache(cache_key) == {"ok": True}
