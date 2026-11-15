"""
Configuration module for menyene-mine.

This module provides a modular configuration system that loads settings from:
1. YAML configuration files (e.g., config/local/settings.yaml)
2. Environment variables (for secrets and overrides)

The configuration system supports:
- Environment-specific configurations (local, prod, staging, etc.)
- Environment variable interpolation in YAML files (e.g., $MISTRAL_API_KEY)
- Type validation using Pydantic models
- Backward compatibility with existing imports

Usage:
    from src.config import Settings, get_settings

    settings = get_settings()
    print(settings.app_name)
"""

from src.config.environment import Environment, get_environment
from src.config.interpolation import resolve_env_vars, resolve_env_vars_in_dict
from src.config.loader import ConfigLoader, get_config_loader
from src.config.models import AIConfig, AppConfig, DatabaseConfig, JudgeConfig, Settings
from src.config.prompt_loader import (
    PromptLoader,
    StaticTemplateLoader,
    get_prompt_loader,
    get_static_template_loader,
    reset_loaders,
)
from src.config.settings import get_settings, reset_settings

__all__ = [
    # Environment
    "Environment",
    "get_environment",
    # Interpolation
    "resolve_env_vars",
    "resolve_env_vars_in_dict",
    # Loader
    "ConfigLoader",
    "get_config_loader",
    # Models
    "AIConfig",
    "AppConfig",
    "DatabaseConfig",
    "JudgeConfig",
    "Settings",
    # Settings
    "get_settings",
    "reset_settings",
    # Prompt loading (backward compatibility)
    "PromptLoader",
    "StaticTemplateLoader",
    "get_prompt_loader",
    "get_static_template_loader",
    "reset_loaders",
]
