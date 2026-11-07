from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

DATABASE_NAME = "menyene_mine"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "menyene-mine"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    database_url: str = f"sqlite+aiosqlite:///./{DATABASE_NAME}.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
