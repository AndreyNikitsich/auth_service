import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"), env_file_encoding="utf-8", extra="ignore"
    )


class ProjectMetadataSettings(EnvSettings):
    project_name: str = Field(default="Auth Service")
    docs_url: str = "/api/openapi"
    openapi_url: str = "/api/openapi.json"
    version: str = "0.1.0"


class TokenSettings(EnvSettings):
    access_token_expire_minutes: int = Field(default=15)
    refresh_token_expire_minutes: int = Field(default=60 * 24 * 2)
    secret_key: str = Field(default="")
    public_key: str | None = None
    algorithm: str = "RS256"
    type: str = "Bearer"


class PostgresSettings(EnvSettings):
    db_user: str = Field(default="app")
    db_password: str = Field(default="123qwe")
    db_host: str = Field(default="localhost")
    db_port: int = Field(default=5432)
    db_name: str = Field(default="auth_db")


class RedisSettings(EnvSettings):
    redis_host: str = Field(default="127.0.0.1")
    redis_port: int = Field(default=6379)
    cache_expire_in_seconds: int = Field(default=(60 * 5))


class Settings(BaseSettings):
    project: ProjectMetadataSettings = ProjectMetadataSettings()
    pg: PostgresSettings = PostgresSettings()
    redis: RedisSettings = RedisSettings()
    token: TokenSettings = TokenSettings()


settings = Settings()
