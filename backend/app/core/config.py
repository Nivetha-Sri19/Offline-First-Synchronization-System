from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Offline-First Synchronization System"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False

    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(
        ...,
        description="SQLAlchemy MySQL connection URL.",
    )

    database_pool_size: int = Field(
        default=10,
        ge=1,
        le=100,
    )

    database_max_overflow: int = Field(
        default=20,
        ge=0,
        le=100,
    )

    database_pool_timeout: int = Field(
        default=30,
        ge=1,
    )

    database_pool_recycle: int = Field(
        default=1800,
        ge=60,
    )

    redis_url: str = Field(
        ...,
        description="Redis connection URL.",
    )

    redis_max_connections: int = Field(
        default=50,
        ge=1,
        le=500,
    )

    jwt_secret_key: str = Field(
        ...,
        min_length=32,
    )

    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
    )

    refresh_token_expire_days: int = Field(
        default=7,
        ge=1,
    )

    cors_origins: str = "*"

    log_level: str = "INFO"

    sync_batch_size: int = Field(
        default=100,
        ge=1,
        le=500,
    )

    sync_max_retries: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    sync_lock_ttl_seconds: int = Field(
        default=30,
        ge=5,
        le=300,
    )

    rate_limit_per_minute: int = Field(
        default=120,
        ge=1,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()