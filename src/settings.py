"""
Application settings with support for YAML configuration and environment variables.

Settings are loaded from:
1. settings.yaml in the config directory (specified by MENYENEMINE_CONFIG_PATH)
2. .env file in the config directory
3. Environment variables

Environment variable placeholders in settings.yaml (e.g., $MISTRAL_API_KEY) are
resolved from the environment or .env file.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    Settings are loaded from:
    1. YAML configuration file (settings.yaml)
    2. .env file in config directory
    3. Environment variables

    The MENYENEMINE_CONFIG_PATH environment variable specifies the config directory.
    Default: config/local
    """

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application settings
    app_name: str = "menyene-mine"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database
    database_url: str = "sqlite+aiosqlite:///./menyene_mine.db"

    # AI Configuration
    ai_enabled: bool = False
    mistral_api_key: str | None = None
    ai_model: str = "mistral-medium"
    ai_max_drafts: int = 1
    ai_temperature: float = 0.7

    # LLM Judge Configuration
    judge_enabled: bool = True
    judge_model: str | None = None  # Uses ai_model if None
    judge_temperature: float = 0.3
    judge_max_tokens: int = 500

    # Environment
    environment: str = "local"

    @property
    def judge_model_resolved(self) -> str:
        """Get the resolved judge model (falls back to ai_model)."""
        return self.judge_model or self.ai_model


@lru_cache
def get_settings() -> Settings:
    """Get the global settings instance."""
    return Settings()


def reset_settings() -> None:
    """Reset the settings cache (useful for testing)."""
    get_settings.cache_clear()
