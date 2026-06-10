from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ALLOWED_ENVIRONMENTS = {"development", "test", "production"}
WEAK_SECRET_KEYS = {"change-me", "changeme", "secret", "test", "password"}


class Settings(BaseSettings):
    app_name: str = "Starter Backend Template"
    environment: str = "development"
    database_url: str = Field(
        default="postgresql://app_user:app_password@db:5432/app_db"
    )
    secret_key: str = Field(min_length=1)
    algorithm: str = "HS256"
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    log_level: str = "INFO"
    rate_limit_default_limit: int = Field(default=5, gt=0)
    rate_limit_default_window_seconds: int = Field(default=60, gt=0)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    test_database_url: str = Field(
        default="postgresql://app_user:app_password@test_db:5432/app_test_db"
    )

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        normalized_environment = value.lower()

        if normalized_environment not in ALLOWED_ENVIRONMENTS:
            allowed_values = ", ".join(sorted(ALLOWED_ENVIRONMENTS))
            raise ValueError(f"environment must be one of: {allowed_values}")

        return normalized_environment

    @model_validator(mode="after")
    def validate_secret_key(self) -> "Settings":
        secret_key = self.secret_key.strip()

        if secret_key.lower() in WEAK_SECRET_KEYS:
            raise ValueError("secret_key must not use a known weak placeholder")

        if self.environment == "production" and len(secret_key) < 32:
            raise ValueError(
                "secret_key must be at least 32 characters in production"
            )

        return self

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.upper()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
