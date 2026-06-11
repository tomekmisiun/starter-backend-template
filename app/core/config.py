from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ALLOWED_ENVIRONMENTS = {"development", "test", "staging", "production"}
WEAK_SECRET_KEYS = {"change-me", "changeme", "secret", "test", "password"}
LOCAL_DATABASE_URL = "postgresql://app_user:app_password@db:5432/app_db"
LOCAL_PASSWORD_RESET_URLS = {
    "http://localhost:8000/reset-password",
    "http://127.0.0.1:8000/reset-password",
}
LOCAL_S3_ENDPOINT_URLS = {
    "http://minio:9000",
    "http://localhost:9000",
    "http://127.0.0.1:9000",
}
LOCAL_S3_CREDENTIALS = {"minioadmin"}
PLACEHOLDER_EMAILS = {"noreply@example.com"}


class Settings(BaseSettings):
    app_name: str = "Starter Backend Template"
    environment: str = "development"
    database_url: str = Field(default=LOCAL_DATABASE_URL)
    secret_key: str = Field(min_length=1)
    algorithm: str = "HS256"
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    log_level: str = "INFO"
    rate_limit_default_limit: int = Field(default=5, gt=0)
    rate_limit_default_window_seconds: int = Field(default=60, gt=0)
    password_reset_rate_limit_limit: int = Field(default=3, gt=0)
    password_reset_rate_limit_window_seconds: int = Field(default=300, gt=0)
    smtp_host: str = ""
    smtp_port: int = Field(default=587, gt=0)
    smtp_username: str = ""
    smtp_password: str = ""
    email_from: str = "noreply@example.com"
    password_reset_url: str = "http://localhost:8000/reset-password"
    password_reset_token_expire_minutes: int = Field(default=30, gt=0)
    worker_queue_name: str = "app_jobs"
    worker_failed_queue_name: str = "app_jobs_failed"
    worker_poll_timeout_seconds: int = Field(default=5, gt=0)
    worker_max_retries: int = Field(default=3, ge=0)
    users_cache_enabled: bool = True
    users_cache_ttl_seconds: int = Field(default=60, gt=0)
    s3_endpoint_url: str = "http://minio:9000"
    s3_access_key_id: str = "minioadmin"
    s3_secret_access_key: str = "minioadmin"
    s3_bucket_name: str = "uploads"
    s3_region_name: str = "us-east-1"
    upload_max_size_bytes: int = Field(default=5_242_880, gt=0)
    upload_allowed_content_types: str = "image/png,image/jpeg,application/pdf"
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    sentry_send_default_pii: bool = False
    sentry_release: str = ""

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
    def validate_production_settings(self) -> "Settings":
        secret_key = self.secret_key.strip()

        if secret_key.lower() in WEAK_SECRET_KEYS:
            raise ValueError("secret_key must not use a known weak placeholder")

        if self.environment != "production":
            return self

        production_errors = []

        if len(secret_key) < 32:
            production_errors.append(
                "secret_key must be at least 32 characters in production",
            )

        if self.database_url == LOCAL_DATABASE_URL:
            production_errors.append(
                "database_url must not use the local Docker default in production",
            )

        if self.smtp_host.strip() == "":
            production_errors.append("smtp_host is required in production")

        if self.smtp_username.strip() == "":
            production_errors.append("smtp_username is required in production")

        if self.smtp_password.strip() == "":
            production_errors.append("smtp_password is required in production")

        if self.email_from.lower() in PLACEHOLDER_EMAILS:
            production_errors.append(
                "email_from must not use the example placeholder in production",
            )

        if self.password_reset_url in LOCAL_PASSWORD_RESET_URLS:
            production_errors.append(
                "password_reset_url must not use a localhost URL in production",
            )

        if self.s3_endpoint_url in LOCAL_S3_ENDPOINT_URLS:
            production_errors.append(
                "s3_endpoint_url must not use a local MinIO URL in production",
            )

        if self.s3_access_key_id in LOCAL_S3_CREDENTIALS:
            production_errors.append(
                "s3_access_key_id must not use the local MinIO default in production",
            )

        if self.s3_secret_access_key in LOCAL_S3_CREDENTIALS:
            production_errors.append(
                "s3_secret_access_key must not use the local MinIO default in production",
            )

        if self.s3_bucket_name == "uploads":
            production_errors.append(
                "s3_bucket_name must not use the local default in production",
            )

        if production_errors:
            raise ValueError("; ".join(production_errors))

        return self

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.upper()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
