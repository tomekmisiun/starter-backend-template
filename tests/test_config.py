import pytest
from pydantic import ValidationError

from app.core.config import Settings


def production_settings_kwargs():
    return {
        "environment": "production",
        "secret_key": "strong-production-secret-key-value",
        "database_url": "postgresql://prod_user:prod_password@postgres:5432/prod_db",
        "smtp_host": "smtp.example.test",
        "smtp_username": "smtp-user",
        "smtp_password": "smtp-password",
        "email_from": "noreply@app.example.test",
        "password_reset_url": "https://app.example.test/reset-password",
        "s3_endpoint_url": "https://s3.example.test",
        "s3_access_key_id": "prod-access-key",
        "s3_secret_access_key": "prod-secret-key",
        "s3_bucket_name": "prod-uploads",
    }


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


def test_settings_accepts_staging_environment():
    settings = Settings(
        _env_file=None,
        environment="staging",
        secret_key="staging-secret",
    )

    assert settings.environment == "staging"


def test_settings_rejects_short_production_secret_key():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            **{
                **production_settings_kwargs(),
                "secret_key": "short-secret",
            },
        )


def test_settings_rejects_local_production_placeholders():
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            _env_file=None,
            environment="production",
            secret_key="strong-production-secret-key-value",
        )

    error_message = str(exc_info.value)

    assert "database_url must not use the local Docker default" in error_message
    assert "smtp_host is required in production" in error_message
    assert "smtp_username is required in production" in error_message
    assert "smtp_password is required in production" in error_message
    assert "email_from must not use the example placeholder" in error_message
    assert "password_reset_url must not use a localhost URL" in error_message
    assert "s3_endpoint_url must not use a local MinIO URL" in error_message
    assert "s3_access_key_id must not use the local MinIO default" in error_message
    assert "s3_secret_access_key must not use the local MinIO default" in error_message
    assert "s3_bucket_name must not use the local default" in error_message


def test_settings_accepts_strong_production_secret_key():
    settings = Settings(
        _env_file=None,
        **production_settings_kwargs(),
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
