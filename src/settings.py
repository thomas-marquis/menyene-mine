from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

DATABASE_NAME = "menyene_mine"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "menyene-mine"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    database_url: str = f"sqlite+aiosqlite:///./{DATABASE_NAME}.db"

    # AI Configuration
    ai_enabled: bool = False
    mistral_api_key: str | None = None
    ai_model: str = "mistral-medium"
    ai_max_drafts: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()
