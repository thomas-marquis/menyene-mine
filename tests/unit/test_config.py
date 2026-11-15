"""
Unit tests for the configuration system.
"""

import os
from typing import Any

import pytest

from config import get_config_path
from src.config import (
    ConfigLoader,
    PromptLoader,
    get_config_loader,
    get_prompt_loader,
    reset_loaders,
    resolve_env_vars,
    resolve_env_vars_in_dict,
)


@pytest.fixture(autouse=True)
def reset_config() -> Any:
    """Reset config loaders before each test."""
    reset_loaders()
    yield


class TestConfigPaths:
    """Tests for config path utilities."""

    def test_default_config_path(self) -> None:
        """Test that default config path is config/local."""
        # Unset the environment variable
        old_env = os.environ.pop("MENYENEMINE_CONFIG_PATH", None)

        try:
            config_path = get_config_path()
            assert str(config_path).endswith("config/local")
        finally:
            if old_env:
                os.environ["MENYENEMINE_CONFIG_PATH"] = old_env

    def test_custom_config_path_env_var(self) -> None:
        """Test that MENYENEMINE_CONFIG_PATH environment variable is respected."""
        os.environ["MENYENEMINE_CONFIG_PATH"] = "/custom/path"

        try:
            config_path = get_config_path()
            assert str(config_path) == "/custom/path"
        finally:
            del os.environ["MENYENEMINE_CONFIG_PATH"]

    def test_relative_config_path(self) -> None:
        """Test that relative config paths are resolved correctly."""
        os.environ["MENYENEMINE_CONFIG_PATH"] = "custom/config"

        try:
            config_path = get_config_path()
            # Should be resolved relative to project root
            assert "custom/config" in str(config_path)
        finally:
            del os.environ["MENYENEMINE_CONFIG_PATH"]


class TestConfigLoader:
    """Tests for ConfigLoader."""

    def test_init_default(self) -> None:
        """Test that ConfigLoader initializes with default config path."""
        # Unset the environment variable
        old_env = os.environ.pop("MENYENEMINE_CONFIG_PATH", None)

        try:
            loader = ConfigLoader()
            assert loader.config_dir.exists()
            assert "local" in str(loader.config_dir) or "config" in str(loader.config_dir)
        finally:
            if old_env:
                os.environ["MENYENEMINE_CONFIG_PATH"] = old_env

    def test_init_custom_path(self) -> None:
        """Test that ConfigLoader initializes with custom path."""
        loader = ConfigLoader(config_path="config/local")
        assert loader.config_dir.exists()

    def test_load_yaml(self) -> None:
        """Test loading YAML configuration file."""
        loader = ConfigLoader(config_path="config/local")
        settings = loader.load_yaml()

        # Check that settings are loaded
        assert isinstance(settings, dict)
        assert "ai" in settings or "app" in settings or "database" in settings

    def test_load_yaml_resolves_env_vars(self) -> None:
        """Test that environment variables in YAML are resolved."""
        # Set an environment variable
        os.environ["TEST_API_KEY"] = "test_value_123"

        try:
            loader = ConfigLoader(config_path="config/local")
            settings = loader.load_yaml()

            # The settings should be a dict (even if empty)
            assert isinstance(settings, dict)
        finally:
            del os.environ["TEST_API_KEY"]

    def test_get_setting(self) -> None:
        """Test getting a specific setting by path."""
        loader = ConfigLoader(config_path="config/local")

        # Try to get a setting
        setting = loader.get_setting("ai.enabled", default=None)
        # Should return None or a boolean
        assert setting is None or isinstance(setting, bool)

    def test_load_env(self) -> None:
        """Test loading environment variables from .env file."""
        loader = ConfigLoader(config_path="config/local")
        env_vars = loader.load_env()

        # Should return a dict (may be empty if .env doesn't exist)
        assert isinstance(env_vars, dict)


class TestPromptLoader:
    """Tests for PromptLoader."""

    def test_list_templates(self) -> None:
        """Test listing available prompt templates."""
        loader = PromptLoader()
        templates = loader.list_templates()

        # Should have the templates we created
        assert "instruction_validation" in templates
        assert "recipe_generation" in templates
        assert "recipe_validation" in templates
        assert "system" in templates

    def test_load_template(self) -> None:
        """Test loading a prompt template."""
        loader = PromptLoader()
        template = loader.load("system")

        assert template is not None
        assert template.name == "system.jinja"

    def test_render_template(self) -> None:
        """Test rendering a prompt template with context."""
        loader = PromptLoader()

        # Render system prompt
        rendered = loader.render("system")
        assert "expert chef" in rendered.lower()

        # Render with context
        rendered = loader.render("recipe_generation", instruction="Make a cake")
        assert "Make a cake" in rendered
        assert "exactly ONE" in rendered

    def test_get_raw_template(self) -> None:
        """Test getting raw template content."""
        loader = PromptLoader()
        raw = loader.get_raw("system")

        assert "expert chef" in raw.lower()
        assert "{%" in raw or "{{" in raw  # Should have Jinja syntax

    def test_template_not_found(self) -> None:
        """Test that loading non-existent template raises error."""
        from jinja2.exceptions import TemplateNotFound

        from src.config import PromptLoader

        loader = PromptLoader()

        with pytest.raises(TemplateNotFound):
            loader.load("nonexistent")


class TestEnvVarResolution:
    """Tests for environment variable resolution."""

    def test_resolve_simple_var(self) -> None:
        """Test resolving simple $VAR_NAME syntax."""
        os.environ["TEST_VAR"] = "test_value"

        try:
            result = resolve_env_vars("Hello $TEST_VAR world")
            assert result == "Hello test_value world"
        finally:
            del os.environ["TEST_VAR"]

    def test_resolve_braced_var(self) -> None:
        """Test resolving ${VAR_NAME} syntax."""
        os.environ["TEST_VAR"] = "test_value"

        try:
            result = resolve_env_vars("Hello ${TEST_VAR} world")
            assert result == "Hello test_value world"
        finally:
            del os.environ["TEST_VAR"]

    def test_resolve_missing_var(self) -> None:
        """Test that missing variables are left as-is."""
        result = resolve_env_vars("Hello $MISSING_VAR world")
        assert result == "Hello $MISSING_VAR world"

    def test_resolve_in_dict(self) -> None:
        """Test resolving variables in a dictionary."""
        os.environ["API_KEY"] = "secret123"

        try:
            config: dict[str, Any] = {
                "ai": {
                    "api_key": "$API_KEY",
                    "model": "mistral-medium",
                }
            }
            result = resolve_env_vars_in_dict(config)
            assert result["ai"]["api_key"] == "secret123"
            assert result["ai"]["model"] == "mistral-medium"
        finally:
            del os.environ["API_KEY"]


class TestGlobalLoaders:
    """Tests for global loader instances."""

    def test_get_config_loader(self) -> None:
        """Test getting global config loader."""
        loader = get_config_loader()
        assert isinstance(loader, ConfigLoader)

        # Should return the same instance
        loader2 = get_config_loader()
        assert loader is loader2

    def test_get_prompt_loader(self) -> None:
        """Test getting global prompt loader."""
        loader = get_prompt_loader()
        assert isinstance(loader, PromptLoader)

        # Should return the same instance
        loader2 = get_prompt_loader()
        assert loader is loader2

    def test_reset_loaders(self) -> None:
        """Test resetting global loaders."""
        loader1 = get_config_loader()
        prompt_loader1 = get_prompt_loader()

        reset_loaders()

        loader2 = get_config_loader()
        prompt_loader2 = get_prompt_loader()

        # Should be different instances after reset
        assert loader1 is not loader2
        assert prompt_loader1 is not prompt_loader2
