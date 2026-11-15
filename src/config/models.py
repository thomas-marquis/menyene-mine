"""
Pydantic models for configuration validation.

This module defines the data models for application configuration using Pydantic.
These models provide:
- Type validation for configuration values
- Default values for optional settings
- Nested configuration structure
- Easy access to configuration sections
"""

from pydantic import BaseModel, Field, field_validator

from src.config.environment import get_environment


class AppConfig(BaseModel):
    """Application configuration."""

    name: str = "menyene-mine"
    debug: bool = False
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"])


class DatabaseConfig(BaseModel):
    """Database configuration."""

    url: str = "sqlite+aiosqlite:///./menyene_mine.db"


class AIConfig(BaseModel):
    """AI configuration."""

    enabled: bool = False
    model: str = "mistral-medium"
    max_drafts: int = 1
    temperature: float = 0.7
    api_key: str | None = None

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate that temperature is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Temperature must be between 0 and 1")
        return v


class JudgeConfig(BaseModel):
    """LLM Judge configuration."""

    enabled: bool = True
    model: str | None = None  # Uses ai.model if None
    temperature: float = 0.3
    max_tokens: int = 500

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate that temperature is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Temperature must be between 0 and 1")
        return v

    @property
    def model_resolved(self) -> str:
        """Get the resolved judge model (falls back to ai.model if not set)."""
        # This will be resolved in the Settings class
        return self.model or ""


class Settings(BaseModel):
    """
    Root configuration model for menyene-mine.

    This model combines all configuration sections and provides
    the main interface for accessing application settings.

    Attributes:
        app: Application configuration
        database: Database configuration
        ai: AI configuration
        judge: LLM Judge configuration
    """

    app: AppConfig = Field(default_factory=AppConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    judge: JudgeConfig = Field(default_factory=JudgeConfig)

    @property
    def app_name(self) -> str:
        """Get the application name (backward compatibility)."""
        return self.app.name

    @property
    def debug(self) -> bool:
        """Get the debug flag (backward compatibility)."""
        return self.app.debug

    @property
    def cors_origins(self) -> list[str]:
        """Get the CORS origins (backward compatibility)."""
        return self.app.cors_origins

    @property
    def database_url(self) -> str:
        """Get the database URL (backward compatibility)."""
        return self.database.url

    @property
    def ai_enabled(self) -> bool:
        """Get the AI enabled flag (backward compatibility)."""
        return self.ai.enabled

    @property
    def mistral_api_key(self) -> str | None:
        """Get the Mistral API key (backward compatibility)."""
        return self.ai.api_key

    @property
    def ai_model(self) -> str:
        """Get the AI model (backward compatibility)."""
        return self.ai.model

    @property
    def ai_max_drafts(self) -> int:
        """Get the AI max drafts (backward compatibility)."""
        return self.ai.max_drafts

    @property
    def ai_temperature(self) -> float:
        """Get the AI temperature (backward compatibility)."""
        return self.ai.temperature

    @property
    def judge_enabled(self) -> bool:
        """Get the judge enabled flag (backward compatibility)."""
        return self.judge.enabled

    @property
    def judge_model(self) -> str | None:
        """Get the judge model (backward compatibility)."""
        return self.judge.model

    @judge_model.setter
    def judge_model(self, value: str | None) -> None:
        """Set the judge model (backward compatibility)."""
        self.judge.model = value

    @property
    def judge_temperature(self) -> float:
        """Get the judge temperature (backward compatibility)."""
        return self.judge.temperature

    @property
    def judge_max_tokens(self) -> int:
        """Get the judge max tokens (backward compatibility)."""
        return self.judge.max_tokens

    @property
    def judge_model_resolved(self) -> str:
        """Get the resolved judge model (falls back to ai.model if not set)."""
        return self.judge.model or self.ai.model

    @property
    def environment(self) -> str:
        """Get the current environment (backward compatibility)."""
        return get_environment().value
