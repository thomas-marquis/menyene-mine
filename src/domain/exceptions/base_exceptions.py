"""
Base domain exceptions.

All domain-specific exceptions inherit from DomainException.
"""


class DomainException(Exception):
    """
    Base exception for all domain-specific errors.

    All custom domain exceptions should inherit from this class.
    This allows for consistent error handling at the controller level.
    """

    def __init__(self, message: str) -> None:
        """
        Initialize the domain exception.

        Args:
            message: Error message describing the issue
        """
        super().__init__(message)
        self.message = message


class InvalidInstructionError(DomainException):
    """
    Exception raised when an instruction is invalid.

    This is raised by the LLM Judge when instruction validation fails.
    """

    def __init__(self, message: str) -> None:
        """
        Initialize the invalid instruction error.

        Args:
            message: Reason why the instruction is invalid
        """
        super().__init__(message)


class RecipeValidationError(DomainException):
    """
    Exception raised when recipe validation fails.

    This is raised by the LLM Judge when recipe validation fails.
    """

    def __init__(self, message: str, issues: list[str] | None = None) -> None:
        """
        Initialize the recipe validation error.

        Args:
            message: Reason why the recipe is invalid
            issues: List of specific issues found during validation
        """
        super().__init__(message)
        self.issues = issues or []


class RecipeGenerationError(DomainException):
    """
    Exception raised when recipe generation fails.

    This is raised when the AI generator fails to produce valid recipes.
    """

    def __init__(self, message: str) -> None:
        """
        Initialize the recipe generation error.

        Args:
            message: Reason why recipe generation failed
        """
        super().__init__(message)
