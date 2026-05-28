import os


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://app_user:app_password@localhost:5432/app_db",
    )
    environment: str = os.getenv("ENVIRONMENT", "development")
    secret_key: str = os.getenv("SECRET_KEY", "change-me")


settings = Settings()