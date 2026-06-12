from datetime import timedelta

from jose import jwt

from app.core.config import settings
from app.core.security import create_access_token, decode_token


def test_access_token_uses_settings_algorithm_for_encode_and_decode():
    token = create_access_token(
        subject="user@example.com",
        tenant_id=1,
        token_version=1,
        expires_delta=timedelta(minutes=5),
    )

    payload = decode_token(token)

    assert payload["sub"] == "user@example.com"
    assert jwt.get_unverified_header(token)["alg"] == settings.algorithm
