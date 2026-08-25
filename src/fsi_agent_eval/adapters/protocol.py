"""Agent adapter protocol and base types.

The AgentAdapter protocol defines the interface that any agent provider
must implement. Gate logic and evaluators consume only the AgentRunResult
contract — never provider-specific objects.
"""

from __future__ import annotations

from typing import Any, ClassVar, Protocol, runtime_checkable

from pydantic import BaseModel, Field

from fsi_agent_eval.contracts.agent import AgentRunResult


class TestCase(BaseModel):
    """A single evaluation test case to send to an agent."""

    __test__: ClassVar[bool] = False

    id: str = Field(description="Unique test case identifier (maps to traceability matrix).")
    requirement_id: str = Field(description="Requirement being tested.")
    requirement_ids: list[str] = Field(
        default_factory=list,
        description="Additional requirement IDs exercised by this case.",
    )
    conversation_turns: list[str] = Field(
        description="User messages in sequence (multi-turn conversation)."
    )
    expected_tool_sequence: list[str] | None = Field(
        default=None, description="Expected tool-call names in order, if applicable."
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def all_requirement_ids(self) -> list[str]:
        """Return stable, de-duplicated requirement links."""
        return list(dict.fromkeys([self.requirement_id, *self.requirement_ids]))


@runtime_checkable
class AgentAdapter(Protocol):
    """Protocol for agent providers.

    Implementations accept a test case and return a normalized AgentRunResult.
    Provider-specific initialization (credentials, endpoints) is handled in
    the concrete implementation's constructor.
    """

    def run(self, test_case: TestCase) -> AgentRunResult:
        """Execute a test case against the agent and return normalized results."""
        ...
