"""Trace normalization contracts.

These models represent the intermediate trace format extracted from provider
responses before being assembled into AgentRunResult.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RawToolCallTrace(BaseModel):
    """A raw tool-call trace as extracted from a provider, before normalization.

    This exists to decouple extraction (provider-specific) from normalization
    (provider-agnostic). Adapters produce these; the normalizer converts them
    to ToolCallRecord.
    """

    provider_call_id: str = Field(description="Provider-assigned call ID.")
    tool_name: str
    arguments_raw: str = Field(description="Raw argument string (JSON) from provider.")
    output_raw: str | None = Field(
        default=None,
        description=(
            "Raw output string as submitted via tool outputs. "
            "None if output was not captured or call errored."
        ),
    )
    error: str | None = None
    step_id: str | None = Field(default=None, description="RunStep ID from provider.")
    step_created_at: datetime | None = None
    step_completed_at: datetime | None = None


class NormalizedTrace(BaseModel):
    """A full normalized trace for one agent run.

    Contains both the ordered tool-call sequence and run-level metadata
    extracted from provider traces.
    """

    run_id: str
    thread_id: str | None = None
    agent_id: str | None = None
    model: str | None = None
    tool_call_traces: list[RawToolCallTrace] = Field(default_factory=list)
    run_started_at: datetime | None = None
    run_completed_at: datetime | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    raw_steps: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Serialized RunStep dicts for diagnostic purposes only.",
    )
