"""
Domain exceptions module.

Contains all domain-specific exceptions for the application.
"""

from .base_exceptions import (
    DomainException,
    InvalidInstructionError,
    RecipeGenerationError,
    RecipeValidationError,
)

__all__ = [
    "DomainException",
    "InvalidInstructionError",
    "RecipeGenerationError",
    "RecipeValidationError",
]
