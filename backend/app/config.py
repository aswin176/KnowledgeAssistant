"""Application configuration with environment profiles."""

from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Knowledge Assistant"
    app_env: AppEnv = AppEnv.DEVELOPMENT
    debug: bool = False
    secret_key: str = Field(default="change-me-in-production")
    api_prefix: str = "/api/v1"

    host: str = "0.0.0.0"
    port: int = 8000

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4j"
    neo4j_database: str = "neo4j"

    jwt_secret_key: str = Field(default="change-me-jwt-secret")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    admin_username: str = "admin"
    admin_password: str = "admin123"

    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4096

    redis_url: str = "redis://localhost:6379/0"
    celery_enabled: bool = False

    rate_limit: str = "60/minute"

    upload_dir: Path = Path("./uploads")
    max_upload_size_mb: int = 50
    import_file_path: str = "./uploads/persons.xlsx"

    log_level: str = "INFO"
    log_dir: Path = Path("./logs")

    telegram_bot_token: str = ""
    telegram_enabled: bool = False

    cors_origins: str = "http://localhost:3000"

    @field_validator("upload_dir", "log_dir", mode="before")
    @classmethod
    def parse_path(cls, v: str | Path) -> Path:
        return Path(v)

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def is_testing(self) -> bool:
        return self.app_env == AppEnv.TESTING

    @property
    def is_production(self) -> bool:
        return self.app_env == AppEnv.PRODUCTION


Profile = Literal["development", "production", "testing"]


@lru_cache
def get_settings(profile: Profile | None = None) -> Settings:
    """Return cached settings instance."""
    env_file = ".env"
    if profile:
        profile_file = f".env.{profile}"
        if Path(profile_file).exists():
            env_file = profile_file
    return Settings(_env_file=env_file)  # type: ignore[call-arg]
