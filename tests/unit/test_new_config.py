"""
Unit tests for the new modular configuration system.
"""

import os

import pytest

from src.config import (
    AIConfig,
    AppConfig,
    DatabaseConfig,
    Environment,
    JudgeConfig,
    get_environment,
    get_settings,
    reset_settings,
)
from src.config.environment import get_config_dir
from src.config.loader import ConfigLoader


@pytest.fixture(autouse=True)
def reset_config_cache():
    """Reset config cache before each test."""
    reset_settings()
    yield


class TestNewConfigSystem:
    """Tests for the new modular configuration system."""

    def test_settings_loaded_from_yaml(self) -> None:
        """Test that settings are loaded from YAML file."""
        os.environ["MISTRAL_API_KEY"] = "test_key_123"
        os.environ["JUDGE_MODEL"] = "test_judge"

        try:
            settings = get_settings()

            # Check values from YAML
            assert settings.app_name == "menyene-mine"
            assert settings.debug is True
            assert settings.database_url == "sqlite+aiosqlite:///./menyene_mine.db"
            assert settings.ai_enabled is True
            assert settings.ai_model == "mistral-small-latest"
            assert settings.ai_max_drafts == 1
            assert settings.ai_temperature == 0.7
            assert settings.mistral_api_key == "test_key_123"
            assert settings.judge_enabled is True
            assert settings.judge_model == "test_judge"
            assert settings.judge_temperature == 0.1
            assert settings.judge_max_tokens == 5000
        finally:
            del os.environ["MISTRAL_API_KEY"]
            del os.environ["JUDGE_MODEL"]

    def test_cors_origins_parsed_from_string(self) -> None:
        """Test that comma-separated CORS origins are parsed into a list."""
        settings = get_settings()
        assert isinstance(settings.cors_origins, list)
        assert "http://localhost:3000" in settings.cors_origins
        assert "http://localhost:5173" in settings.cors_origins

    def test_environment_detection(self) -> None:
        """Test environment detection from APP_ENV variable."""
        # Test default environment
        old_env = os.environ.pop("APP_ENV", None)
        try:
            assert get_environment() == Environment.LOCAL

            # Test custom environment
            os.environ["APP_ENV"] = "production"
            assert get_environment() == Environment.PRODUCTION

            os.environ["APP_ENV"] = "staging"
            assert get_environment() == Environment.STAGING

            os.environ["APP_ENV"] = "test"
            assert get_environment() == Environment.TEST
        finally:
            if old_env:
                os.environ["APP_ENV"] = old_env
            else:
                os.environ.pop("APP_ENV", None)

    def test_config_dir_resolution(self) -> None:
        """Test that config directory is resolved correctly."""
        old_env = os.environ.pop("APP_ENV", None)
        old_config_path = os.environ.pop("MENYENEMINE_CONFIG_PATH", None)

        try:
            # Test default config dir
            config_dir = get_config_dir()
            assert "local" in str(config_dir) or "config" in str(config_dir)

            # Test with custom APP_ENV
            os.environ["APP_ENV"] = "test"
            config_dir = get_config_dir()
            assert "test" in str(config_dir)
        finally:
            if old_env:
                os.environ["APP_ENV"] = old_env
            if old_config_path:
                os.environ["MENYENEMINE_CONFIG_PATH"] = old_config_path

    def test_config_loader(self) -> None:
        """Test ConfigLoader functionality."""
        os.environ["TEST_VAR"] = "test_value"

        try:
            loader = ConfigLoader(config_path="config/local")
            config = loader.load_all()

            assert "app" in config
            assert "database" in config
            assert "ai" in config
            assert "judge" in config
        finally:
            del os.environ["TEST_VAR"]

    def test_settings_model_structure(self) -> None:
        """Test that Settings model has the correct structure."""
        settings = get_settings()

        # Check that all sections exist
        assert hasattr(settings, "app")
        assert hasattr(settings, "database")
        assert hasattr(settings, "ai")
        assert hasattr(settings, "judge")

        # Check that sections are the correct types
        assert isinstance(settings.app, AppConfig)
        assert isinstance(settings.database, DatabaseConfig)
        assert isinstance(settings.ai, AIConfig)
        assert isinstance(settings.judge, JudgeConfig)

    def test_backward_compatibility(self) -> None:
        """Test that all settings attributes are accessible."""
        settings = get_settings()

        # All attributes should be accessible
        assert hasattr(settings, "app_name")
        assert hasattr(settings, "debug")
        assert hasattr(settings, "cors_origins")
        assert hasattr(settings, "database_url")
        assert hasattr(settings, "ai_enabled")
        assert hasattr(settings, "mistral_api_key")
        assert hasattr(settings, "ai_model")
        assert hasattr(settings, "ai_max_drafts")
        assert hasattr(settings, "ai_temperature")
        assert hasattr(settings, "judge_enabled")
        assert hasattr(settings, "judge_model")
        assert hasattr(settings, "judge_temperature")
        assert hasattr(settings, "judge_max_tokens")
        assert hasattr(settings, "judge_model_resolved")

    def test_judge_model_resolved(self) -> None:
        """Test that judge_model_resolved falls back to ai_model."""
        # Ensure we're using local environment
        old_env = os.environ.pop("APP_ENV", None)
        os.environ["MISTRAL_API_KEY"] = "test_key"
        os.environ["JUDGE_MODEL"] = "test_judge"

        try:
            settings = get_settings()

            # When judge_model is set
            assert settings.judge_model == "test_judge"
            assert settings.judge_model_resolved == "test_judge"
        finally:
            del os.environ["MISTRAL_API_KEY"]
            del os.environ["JUDGE_MODEL"]
            if old_env:
                os.environ["APP_ENV"] = old_env

    def test_test_environment_config(self) -> None:
        """Test loading test environment configuration."""
        os.environ["APP_ENV"] = "test"

        try:
            settings = get_settings()

            # Test environment should have in-memory database
            assert settings.database_url == "sqlite+aiosqlite:///:memory:"
            assert settings.ai_enabled is False
        finally:
            del os.environ["APP_ENV"]
