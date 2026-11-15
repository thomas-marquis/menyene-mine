"""
Prompt loading utilities for menyene-mine.

This module provides functionality for loading and rendering Jinja2 prompt templates.
It is kept for backward compatibility with the old config.py module.
"""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

from src.config.environment import get_config_dir
from src.config.loader import reset_config_loader


class PromptLoader:
    """Loads and renders Jinja2 prompt templates."""

    def __init__(self, config_path: str | None = None) -> None:
        """
        Initialize the prompt loader.

        Args:
            config_path: Optional path to configuration directory
        """
        if config_path:
            self._config_dir = Path(config_path)
        else:
            self._config_dir = get_config_dir()

        self._prompts_dir = self._config_dir / "prompts"

        # Ensure prompts directory exists
        if not self._prompts_dir.exists():
            raise FileNotFoundError(f"Prompts directory not found: {self._prompts_dir}")

        # Set up Jinja2 environment
        self._jinja_env = Environment(
            loader=FileSystemLoader(str(self._prompts_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

    def load(self, template_name: str) -> Template:
        """
        Load a prompt template.

        Args:
            template_name: Name of the template file (without .jinja extension)

        Returns:
            Jinja2 Template object
        """
        if not template_name.endswith(".jinja"):
            template_name += ".jinja"

        return self._jinja_env.get_template(template_name)

    def render(self, template_name: str, **context: Any) -> str:
        """
        Load and render a prompt template with context.

        Args:
            template_name: Name of the template file (without .jinja extension)
            **context: Variables to pass to the template

        Returns:
            Rendered prompt string
        """
        template = self.load(template_name)
        return template.render(**context)

    def get_raw(self, template_name: str) -> str:
        """
        Get the raw template content without rendering.

        Args:
            template_name: Name of the template file

        Returns:
            Raw template content
        """
        if not template_name.endswith(".jinja"):
            template_name += ".jinja"

        template_path = self._prompts_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        return template_path.read_text()

    def list_templates(self) -> list[str]:
        """
        List all available prompt templates.

        Returns:
            List of template names (without .jinja extension)
        """
        templates = []
        for file in self._prompts_dir.glob("*.jinja"):
            templates.append(file.stem)
        return sorted(templates)


class StaticTemplateLoader:
    """Loads and renders Jinja2 templates from the resources/templates directory."""

    def __init__(self, base_path: str | None = None) -> None:
        """
        Initialize the static template loader.

        Args:
            base_path: Optional base path to the project root
        """

        if base_path:
            self._base_path = Path(base_path)
        else:
            self._base_path = Path(__file__).parent.parent.parent

        self.templates_dir = self._base_path / "resources" / "templates"

        if not self.templates_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {self.templates_dir}")

        self._jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

    def load(self, template_name: str) -> Template:
        """
        Load a static template.

        Args:
            template_name: Name of the template file (without .jinja extension)

        Returns:
            Jinja2 Template object
        """

        if not template_name.endswith(".jinja"):
            template_name += ".jinja"

        return self._jinja_env.get_template(template_name)

    def render(self, template_name: str, **context: Any) -> str:
        """
        Load and render a static template with context.

        Args:
            template_name: Name of the template file (without .jinja extension)
            **context: Variables to pass to the template

        Returns:
            Rendered template string
        """

        template = self.load(template_name)
        return template.render(**context)


# Global instances (lazy initialization)
_config_loader: PromptLoader | None = None
_prompt_loader: PromptLoader | None = None
_static_template_loader: StaticTemplateLoader | None = None


def get_prompt_loader(config_path: str | None = None) -> PromptLoader:
    """Get the global prompt loader instance."""
    global _prompt_loader
    if _prompt_loader is None:
        _prompt_loader = PromptLoader(config_path)
    return _prompt_loader


def get_static_template_loader(base_path: str | None = None) -> StaticTemplateLoader:
    """Get the global static template loader instance."""
    global _static_template_loader
    if _static_template_loader is None:
        _static_template_loader = StaticTemplateLoader(base_path)
    return _static_template_loader


def reset_loaders() -> None:
    """Reset the global loader instances (useful for testing)."""
    global _prompt_loader, _static_template_loader
    _prompt_loader = None
    _static_template_loader = None
    # Also reset the config loader

    reset_config_loader()
