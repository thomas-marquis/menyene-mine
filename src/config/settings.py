"""
Main Settings class for menyene-mine.

This module provides the main Settings class that:
- Loads configuration from YAML files
- Validates configuration using Pydantic models
- Provides backward compatibility with existing code
- Supports environment-specific configurations
"""

from functools import lru_cache
from typing import Any

from src.config.loader import get_config_loader, reset_config_loader
from src.config.models import Settings as SettingsModel


class Settings(SettingsModel):
    """
    Application settings for menyene-mine.

    Settings are loaded from:
    1. YAML configuration file (config/<env>/settings.yaml)
    2. Environment variables (for secrets and overrides)

    The configuration is validated using Pydantic models.

    Example:
        from src.config import Settings, get_settings

        settings = get_settings()
        print(settings.app_name)
        print(settings.ai.enabled)
    """

    pass


@lru_cache
def get_settings() -> Settings:
    """
    Get the global settings instance.

    This function:
    1. Loads the configuration from YAML files
    2. Applies environment variable interpolation
    3. Validates the configuration using Pydantic models
    4. Caches the result for subsequent calls

    Returns:
        Settings: The global settings instance

    Note:
        The settings are cached, so subsequent calls return the same instance.
        Use reset_settings() to clear the cache (useful for testing).
    """
    # Load configuration from YAML
    loader = get_config_loader()
    config_dict = loader.load_all()

    # Create and validate settings using Pydantic
    # We need to transform the flat config dict into the nested structure
    # expected by the Settings model
    settings_dict = _transform_config(config_dict)

    return Settings(**settings_dict)


def _transform_config(config: dict[str, Any]) -> dict[str, Any]:
    """
    Transform the configuration dictionary into the nested structure
    expected by the Settings model.

    The YAML config is already in nested format (app, database, ai, judge),
    so we just need to ensure the structure matches the Pydantic models.

    Args:
        config: The configuration dictionary from YAML

    Returns:
        Dictionary with nested structure matching Settings model
    """
    # The YAML is already in the correct nested format
    # We just need to handle special cases like cors_origins
    result = {
        "app": config.get("app", {}),
        "database": config.get("database", {}),
        "ai": config.get("ai", {}),
        "judge": config.get("judge", {}),
    }

    # Handle cors_origins as comma-separated string
    if "app" in result and "cors_origins" in result["app"]:
        cors = result["app"]["cors_origins"]
        if isinstance(cors, str):
            result["app"]["cors_origins"] = [o.strip() for o in cors.split(",") if o.strip()]

    # Map mistral_api_key to api_key for backward compatibility
    if "ai" in result and "mistral_api_key" in result["ai"]:
        result["ai"]["api_key"] = result["ai"].pop("mistral_api_key")

    return result


def reset_settings() -> None:
    """Reset the settings cache (useful for testing)."""
    get_settings.cache_clear()
    # Also reset the config loader cache

    reset_config_loader()
