from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: Literal["local", "development", "staging", "production"] = "local"
    app_name: str = "Foodbase API"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    database_url: str | None = None
    db_password: SecretStr | None = None
    db_host: str = "db.mpuhtiktoajptolmapgy.supabase.co"
    db_port: int = 5432
    db_name: str = "postgres"
    db_user: str = "postgres"
    db_sslmode: str = "require"
    supabase_url: str | None = "https://mpuhtiktoajptolmapgy.supabase.co"
    supabase_service_role_key: SecretStr | None = None
    admin_token: SecretStr | None = None
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="FOODBASE_",
        case_sensitive=False,
    )

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return _normalize_sqlalchemy_url(self.database_url)

        if self.db_password is None:
            msg = "FOODBASE_DB_PASSWORD is required when FOODBASE_DATABASE_URL is not set."
            raise ValueError(msg)

        return (
            "postgresql+psycopg://"
            f"{quote_plus(self.db_user)}:{quote_plus(self.db_password.get_secret_value())}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?sslmode={quote_plus(self.db_sslmode)}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def _normalize_sqlalchemy_url(raw_url: str) -> str:
    if raw_url.startswith("postgresql+psycopg://"):
        return raw_url
    if raw_url.startswith("postgresql://"):
        return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return raw_url
