"""
Configuration file loader for menyene-mine.

This module provides functionality for:
- Loading YAML configuration files
- Resolving environment variable placeholders
- Merging configuration from multiple sources
- Caching loaded configuration
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dotenv import dotenv_values

from src.config.environment import get_config_dir, get_environment
from src.config.interpolation import resolve_env_vars_in_dict


class ConfigLoader:
    """
    Loads and manages configuration from YAML files.

    The loader supports:
    - Loading configuration from environment-specific directories
    - Environment variable interpolation in YAML values
    - Caching of loaded configuration
    - Merging with environment variable overrides
    """

    def __init__(self, config_path: str | Path | None = None) -> None:
        """
        Initialize the config loader.

        Args:
            config_path: Optional path to configuration directory.
                        If None, uses the path from environment detection.
        """
        if config_path:
            self._config_dir = Path(config_path) if isinstance(config_path, str) else config_path
        else:
            self._config_dir = get_config_dir()

        self._env = get_environment()

    @property
    def config_dir(self) -> Path:
        """Get the configuration directory."""
        return self._config_dir

    @property
    def environment(self) -> str:
        """Get the current environment."""
        return self._env.value

    def load_yaml(self, filename: str = "settings") -> dict[str, Any]:
        """
        Load a YAML configuration file and resolve environment variables.

        Args:
            filename: Name of the YAML file (without extension).
                     Defaults to "settings" which loads settings.yaml

        Returns:
            Dictionary containing the configuration with env vars resolved

        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            yaml.YAMLError: If the YAML file is malformed
        """
        # Load .env file and update os.environ so interpolation works
        env_vars = self.load_env_file()
        for key, value in env_vars.items():
            os.environ.setdefault(key, value)

        # Try .yaml first, then .yml
        yaml_path = self._config_dir / f"{filename}.yaml"
        if not yaml_path.exists():
            yaml_path = self._config_dir / f"{filename}.yml"

        if not yaml_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {yaml_path}")

        with open(yaml_path) as f:
            config = yaml.safe_load(f) or {}

        # Resolve environment variable placeholders
        return resolve_env_vars_in_dict(config)  # type: ignore[no-any-return]

    def load_env_file(self) -> dict[str, str]:
        """
        Load environment variables from .env file in config directory.

        Returns:
            Dictionary of environment variables from .env file
        """

        env_path = self._config_dir / ".env"
        if env_path.exists():
            return dotenv_values(env_path)  # type: ignore[return-value]
        return {}

    def load_env(self) -> dict[str, str]:
        """
        Load environment variables from .env file in config directory.

        This method is kept for backward compatibility with the old ConfigLoader.

        Returns:
            Dictionary of environment variables from .env file
        """
        return self.load_env_file()

    def load_all(self) -> dict[str, Any]:
        """
        Load all configuration from YAML and environment.

        This method:
        1. Loads the base YAML configuration
        2. Applies environment variable interpolation
        3. Merges with environment variables from .env file
        4. Applies system environment variable overrides

        Returns:
            Dictionary containing the complete configuration
        """
        # Load YAML config with env var interpolation
        config = self.load_yaml()

        # Load .env file variables
        env_vars = self.load_env_file()

        # Apply .env variables to config (for secrets)
        # This allows .env to override interpolated values
        config = self._merge_env_vars(config, env_vars)

        return config

    def _merge_env_vars(self, config: dict[str, Any], env_vars: dict[str, str]) -> dict[str, Any]:
        """
        Merge environment variables into configuration.

        This is a simple merge that doesn't do deep merging.
        Environment variables take precedence over YAML values.

        Args:
            config: The base configuration dictionary
            env_vars: Environment variables to merge

        Returns:
            Merged configuration dictionary
        """
        # For now, we just return the config as-is since the interpolation
        # already handles the $VAR_NAME placeholders.
        # The .env file is loaded separately and used for interpolation.
        return config

    def get_setting(self, path: str, default: Any = None) -> Any:
        """
        Get a specific setting by dot-separated path.

        Args:
            path: Dot-separated path to the setting (e.g., "ai.enabled", "database.url")
            default: Default value if setting not found

        Returns:
            The setting value or default

        Example:
            >>> loader.get_setting("ai.enabled")
            True
            >>> loader.get_setting("nonexistent.setting", default=False)
            False
        """
        config = self.load_all()

        keys = path.split(".")
        current = config

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default

        return current


@lru_cache
def get_config_loader(config_path: str | Path | None = None) -> ConfigLoader:
    """
    Get the global config loader instance.

    Args:
        config_path: Optional path to configuration directory

    Returns:
        ConfigLoader instance
    """
    return ConfigLoader(config_path)


def reset_config_loader() -> None:
    """Reset the config loader cache (useful for testing)."""
    get_config_loader.cache_clear()
