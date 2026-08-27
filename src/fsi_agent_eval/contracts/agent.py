"""Normalized contracts for agent interactions.

These models define the provider-agnostic interface that all adapters produce
and all evaluators consume. Gate logic MUST operate only on these contracts,
never on raw provider objects.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ToolCallRecord(BaseModel):
    """A single normalized tool-call record."""

    sequence: int = Field(description="0-based position in the tool-call sequence for this run.")
    tool_name: str = Field(description="Name of the function tool invoked.")
    arguments: dict[str, Any] = Field(
        default_factory=dict, description="Deserialized arguments passed to the tool."
    )
    result: dict[str, Any] | None = Field(
        default=None, description="Deserialized tool result, or None if errored."
    )
    error: str | None = Field(default=None, description="Error message if the tool call failed.")
    start_time: datetime | None = Field(
        default=None, description="When the tool call began (if available from provider)."
    )
    end_time: datetime | None = Field(
        default=None, description="When the tool call completed (if available from provider)."
    )
    authorization_state: str | None = Field(
        default=None,
        description=(
            "Authorization state when relevant (e.g., 'authorized', 'denied', 'not_applicable')."
        ),
    )


class TokenUsage(BaseModel):
    """Token consumption for an agent run."""

    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class AgentRunResult(BaseModel):
    """Normalized result of an agent run against a single test case.

    This is the primary contract between adapters (providers) and evaluators.
    Provider-specific data is preserved only in `raw_provider_evidence` for
    diagnostics; gate logic must not access it.
    """

    run_id: str = Field(description="Unique identifier for this run.")
    agent_version: str = Field(description="Version identifier of the agent under test.")
    prompt_version: str | None = Field(
        default=None, description="Version of the system prompt, if tracked separately."
    )
    model_identifier: str | None = Field(
        default=None, description="Sanitized deployment identifier used for this run."
    )
    final_response: str = Field(description="The agent's final text response to the user.")
    tool_calls: list[ToolCallRecord] = Field(
        default_factory=list, description="Ordered list of tool calls made during the run."
    )
    citations: list[str] = Field(
        default_factory=list, description="Citations or references produced by the agent."
    )
    start_time: datetime | None = Field(default=None, description="When the run started.")
    end_time: datetime | None = Field(default=None, description="When the run completed.")
    token_usage: TokenUsage | None = Field(
        default=None, description="Token consumption for the run."
    )
    errors: list[str] = Field(
        default_factory=list, description="Errors encountered during the run."
    )
    raw_provider_evidence: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Raw provider-specific output for diagnostics only. "
            "Gate logic MUST NOT consume this field."
        ),
    )
