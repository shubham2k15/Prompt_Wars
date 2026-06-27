from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "MindGarden AI"
    app_env: str = "development"
    database_url: str = "sqlite:///./mindgarden.db"
    local_database_url: str = "sqlite:///./mindgarden.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "development-access-secret"
    refresh_secret: str = "development-refresh-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14
    encryption_key: str = "x7vN3Ca5hnWOM2h0ZMVloYh3hA1k3DAg8mx6VJ4Hq4w="
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    cors_origins: str = Field(default="http://localhost:3000")

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

