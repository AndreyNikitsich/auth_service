from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379

    db_dsn: str = "postgres://app:123qwe@localhost:5432/auth_db"

    service_url: str = Field("http://localhost:8000")
    model_config = SettingsConfigDict(env_prefix="test_", env_file=".env", env_file_encoding="utf-8", extra="ignore")


test_settings = TestSettings()
