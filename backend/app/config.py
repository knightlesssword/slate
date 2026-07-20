"""Application configuration, sourced from environment variables."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # SQLite by default; override with DATABASE_URL for another DB.
    database_url: str = "sqlite:///./slate.db"

    # Signing key for access tokens. Override in production via env.
    secret_key: str = "dev-secret-change-me"
    access_token_expire_minutes: int = 60 * 12

    # Comma-separated list of allowed CORS origins for the deployed frontend.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Upload guard rails.
    max_upload_bytes: int = 1_000_000  # ~1 MB

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
