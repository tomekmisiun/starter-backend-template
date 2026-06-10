import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_requires_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_rejects_weak_secret_key():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            secret_key="change-me",
        )


def test_settings_rejects_unknown_environment():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            environment="local",
            secret_key="development-secret",
        )


def test_settings_rejects_short_production_secret_key():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            environment="production",
            secret_key="short-secret",
        )


def test_settings_accepts_strong_production_secret_key():
    settings = Settings(
        _env_file=None,
        environment="production",
        secret_key="strong-production-secret-key-value",
    )

    assert settings.environment == "production"
    assert settings.secret_key == "strong-production-secret-key-value"


def test_settings_accepts_rate_limit_config():
    settings = Settings(
        _env_file=None,
        secret_key="development-secret",
        rate_limit_default_limit=10,
        rate_limit_default_window_seconds=30,
    )

    assert settings.rate_limit_default_limit == 10
    assert settings.rate_limit_default_window_seconds == 30


def test_settings_rejects_non_positive_rate_limit_config():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            secret_key="development-secret",
            rate_limit_default_limit=0,
        )

    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            secret_key="development-secret",
            rate_limit_default_window_seconds=0,
        )
