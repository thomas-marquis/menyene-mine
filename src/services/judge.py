"""
LLM Judge Service for validating instructions and generated content.

Uses Jinja2 templates from the config directory.
"""

from abc import ABC, abstractmethod

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from pydantic import BaseModel

from ..config import get_prompt_loader
from ..domain.exceptions import InvalidInstructionError


class Judge(ABC):
    """Abstract base class for judge services."""

    @abstractmethod
    async def validate_instruction(self, instruction: str, strict: bool = True) -> None:
        """
        Validate that an instruction is recipe-related.

        Args:
            instruction: The user's instruction to validate
            strict: Whether to use strict validation mode

        Raises:
            InvalidInstructionError: If the instruction is invalid
        """
        ...


class InstructionValidationResult(BaseModel):
    """Pydantic model for instruction validation structured output."""

    status: str
    reason: str | None = None


class MockJudge(Judge):
    """
    Mock judge for validating instructions without using LLM.
    Always validates instructions as valid.
    """

    async def validate_instruction(self, instruction: str, strict: bool = True) -> None:
        """
        Mock validation that always passes.

        Args:
            instruction: The user's instruction to validate
            strict: Whether to use strict validation mode (ignored in mock)
        """
        # Mock judge always validates instructions as valid
        return None


class LLMJudge(Judge):
    """
    LLM-based judge for validating instructions.
    Uses Jinja2 templates for validation.
    """

    def __init__(
        self,
        llm: BaseChatModel,
    ) -> None:
        """
        Initialize the LLM judge.

        Args:
            llm: The LLM instance to use for validation
        """
        self._llm = llm

        prompt_loader = get_prompt_loader()
        self._instruction_validation_template = prompt_loader.load("instruction_validation")

    async def validate_instruction(self, instruction: str, strict: bool = True) -> None:
        """
        Validate that an instruction is recipe-related using LLM.

        Args:
            instruction: The user's instruction to validate
            strict: Whether to use strict validation mode

        Raises:
            InvalidInstructionError: If the instruction is invalid
        """
        validation_prompt = self._instruction_validation_template.render(
            instruction=instruction,
            strict_mode=strict,
        )

        messages: list[BaseMessage] = [
            SystemMessage(content="You are a strict recipe instruction validator."),
            HumanMessage(content=validation_prompt),
        ]

        llm_with_structured_output = self._llm.with_structured_output(InstructionValidationResult)

        try:
            response = await llm_with_structured_output.ainvoke(messages)
            validation_result: InstructionValidationResult = response  # type: ignore[assignment]

            if validation_result.status.lower() == "valid":
                return None
            else:
                reason = validation_result.reason or "Invalid instruction"
                raise InvalidInstructionError(reason)
        except Exception as e:
            raise InvalidInstructionError(f"Failed to validate instruction: {str(e)}") from None
