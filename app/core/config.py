from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Starter Backend Template"
    environment: str = "development"
    database_url: str = Field(
        default="postgresql://app_user:app_password@db:5432/app_db"
    )
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    test_database_url: str = Field(
        default="postgresql://app_user:app_password@test_db:5432/app_test_db"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
