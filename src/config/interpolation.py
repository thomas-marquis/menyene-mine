"""
Environment variable interpolation for configuration values.

This module provides utilities for resolving environment variable placeholders
in configuration files. It supports the following syntax:
- $VAR_NAME: Simple variable substitution
- ${VAR_NAME}: Braced variable substitution
- ${VAR_NAME:-default}: Default value if variable is not set
"""

import os
import re
from typing import Any


class InterpolationError(Exception):
    """Raised when there's an error during environment variable interpolation."""

    pass


def resolve_env_vars(text: str) -> str:
    """
    Resolve environment variable placeholders in text.

    Supports:
    - $VAR_NAME: Simple variable substitution
    - ${VAR_NAME}: Braced variable substitution
    - ${VAR_NAME:-default}: Default value if variable is not set

    Args:
        text: Text containing environment variable placeholders

    Returns:
        Text with environment variables resolved

    Example:
        >>> resolve_env_vars("Hello $USER")
        'Hello <username>'
        >>> resolve_env_vars("Model: ${MODEL:-default}")
        'Model: <model_value_or_default>'
    """
    if not text or not isinstance(text, str):
        return text

    # Pattern to match:
    # - $VAR_NAME
    # - ${VAR_NAME}
    # - ${VAR_NAME:-default}
    pattern = r"\$\{?([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}?"

    def replace_var(match: re.Match[str]) -> str:
        var_name = match.group(1)
        default_value = match.group(2)

        # Get environment variable value
        env_value = os.getenv(var_name)

        # If variable not found, use default if provided
        if env_value is None:
            if default_value is not None:
                return default_value
            # Return original placeholder if no default and variable not found
            return match.group(0)

        return env_value

    return re.sub(pattern, replace_var, text)


def resolve_env_vars_in_dict(data: Any) -> Any:
    """
    Recursively resolve environment variable placeholders in a dictionary or list.

    Args:
        data: Dictionary, list, or value containing environment variable placeholders

    Returns:
        Dictionary/list with environment variables resolved

    Example:
        >>> config = {"api_key": "$API_KEY", "nested": {"value": "$VALUE"}}
        >>> resolve_env_vars_in_dict(config)
        {'api_key': '<api_key_value>', 'nested': {'value': '<value>'}}
    """
    if isinstance(data, dict):
        return {k: resolve_env_vars_in_dict(v) for k, v in data.items()}
    if isinstance(data, list):
        return [resolve_env_vars_in_dict(item) for item in data]
    if isinstance(data, str):
        return resolve_env_vars(data)
    return data
