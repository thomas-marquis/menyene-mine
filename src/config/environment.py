"""
Environment detection and management for menyene-mine.

This module handles:
- Detecting the current environment (local, prod, staging, etc.)
- Resolving configuration directory paths based on environment
- Managing environment-specific settings
"""

import os
from enum import StrEnum
from pathlib import Path


class Environment(StrEnum):
    """Supported application environments."""

    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


# Default configuration paths for each environment
ENVIRONMENT_CONFIG_PATHS: dict[Environment, str] = {
    Environment.LOCAL: "config/local",
    Environment.DEVELOPMENT: "config/development",
    Environment.STAGING: "config/staging",
    Environment.PRODUCTION: "config/production",
    Environment.TEST: "config/test",
}

# Environment variable name for specifying the environment
ENV_VAR_NAME = "APP_ENV"

# Environment variable name for overriding the config path
CONFIG_PATH_VAR_NAME = "MENYENEMINE_CONFIG_PATH"


class EnvironmentError(Exception):
    """Raised when there's an error with environment configuration."""

    pass


def get_environment() -> Environment:
    """
    Get the current application environment.

    The environment is determined by:
    1. The APP_ENV environment variable (if set)
    2. Defaults to LOCAL if not specified

    Returns:
        Environment: The current environment

    Raises:
        EnvironmentError: If the specified environment is not valid
    """

    env_value = os.getenv(ENV_VAR_NAME, Environment.LOCAL.value).lower()

    try:
        return Environment(env_value)
    except ValueError as err:
        valid_envs = ", ".join([e.value for e in Environment])
        raise EnvironmentError(f"Invalid environment '{env_value}'. Valid environments are: {valid_envs}") from err


def get_config_dir(env: Environment | None = None) -> Path:
    """
    Get the configuration directory for the specified environment.

    Args:
        env: The environment to get the config directory for.
             If None, uses the current environment.

    Returns:
        Path: The absolute path to the configuration directory
    """

    if env is None:
        env = get_environment()

    # Check if config path is explicitly set via environment variable
    custom_path = os.getenv(CONFIG_PATH_VAR_NAME)
    if custom_path:
        return Path(custom_path).absolute()

    # Get the default path for the environment
    config_path = ENVIRONMENT_CONFIG_PATHS.get(env)
    if config_path is None:
        raise EnvironmentError(f"No default config path defined for environment: {env}")

    # Resolve relative to project root (parent of src directory)
    project_root = Path(__file__).parent.parent.parent
    return (project_root / config_path).absolute()


def get_settings_file_path(env: Environment | None = None) -> Path:
    """
    Get the path to the settings.yaml file for the specified environment.

    Args:
        env: The environment to get the settings file for.
             If None, uses the current environment.

    Returns:
        Path: The absolute path to the settings.yaml file
    """
    config_dir = get_config_dir(env)
    return config_dir / "settings.yaml"


def get_env_file_path(env: Environment | None = None) -> Path:
    """
    Get the path to the .env file for the specified environment.

    Args:
        env: The environment to get the .env file for.
             If None, uses the current environment.

    Returns:
        Path: The absolute path to the .env file
    """
    config_dir = get_config_dir(env)
    return config_dir / ".env"
