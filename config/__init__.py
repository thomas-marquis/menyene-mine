"""
Configuration system for menyene-mine.

This module provides utilities for loading configuration files,
Jinja2 templates, and environment-specific settings.
"""

import os
from pathlib import Path

# Configuration paths
# Config path can be overridden via MENYENEMINE_CONFIG_PATH environment variable
# Default: config/local
DEFAULT_CONFIG_PATH = "config/local"
CONFIG_DIR = Path(__file__).parent.absolute()


def get_config_path() -> Path:
    """
    Get the configuration path from environment variable or use default.

    The environment variable MENYENEMINE_CONFIG_PATH specifies the path to the
    configuration directory. If not set, defaults to 'config/local' relative to
    the project root.

    Returns:
        Path to the configuration directory
    """
    config_path = os.getenv("MENYENEMINE_CONFIG_PATH", DEFAULT_CONFIG_PATH)

    # If it's a relative path, resolve it relative to the project root
    # (which is the parent of the config directory)
    if not os.path.isabs(config_path):
        # Go up from config directory to project root, then into the specified path
        project_root = CONFIG_DIR.parent
        return project_root / config_path

    return Path(config_path)


def get_config_dir() -> Path:
    """Get the current configuration directory."""
    return get_config_path()


def get_prompts_dir() -> Path:
    """Get the prompts directory for the current configuration."""
    return get_config_dir() / "prompts"


def get_env_file_path() -> Path:
    """Get the path to the .env file in the config directory."""
    return get_config_dir() / ".env"


def get_settings_file_path() -> Path:
    """Get the path to the settings.yaml file."""
    return get_config_dir() / "settings.yaml"
