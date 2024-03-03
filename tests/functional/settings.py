from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "auth_db"

    service_url: str = Field("http://127.0.0.1:8000")
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


test_settings = TestSettings()
