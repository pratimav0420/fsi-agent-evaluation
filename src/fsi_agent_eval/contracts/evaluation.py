"""Evaluation result contracts.

These models define the structure that evaluators produce and gate logic
consumes. They are intentionally separate from provider models.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Severity(StrEnum):
    """Severity levels for evaluation findings."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    INFORMATIONAL = "informational"


class EvaluationResult(BaseModel):
    """Result of a single evaluator applied to a single test case."""

    evaluator_name: str
    requirement_id: str = Field(description="Requirement ID from the traceability matrix.")
    test_case_id: str
    passed: bool
    severity: Severity
    score: float | None = Field(default=None, description="Numeric score (0.0–1.0) if applicable.")
    message: str | None = Field(
        default=None, description="Human-readable explanation of the result."
    )
    evidence: dict[str, Any] = Field(
        default_factory=dict,
        description="Supporting evidence (e.g., failed assertion details).",
    )
    evaluated_at: datetime = Field(default_factory=_utcnow)
    evaluator_error: str | None = Field(
        default=None,
        description="Infrastructure/evaluator failure, distinct from an agent finding.",
    )
    must_pass: bool = Field(default=False, description="Whether a failure blocks individually.")


class GateDecision(StrEnum):
    """Possible release gate outcomes."""

    PASS = "pass"
    BLOCK = "block"
    WARN = "warn"
    INCONCLUSIVE = "inconclusive"


class GateResult(BaseModel):
    """Aggregated gate decision for a release candidate."""

    decision: GateDecision
    blocking_results: list[EvaluationResult] = Field(default_factory=list)
    warning_results: list[EvaluationResult] = Field(default_factory=list)
    informational_results: list[EvaluationResult] = Field(default_factory=list)
    summary: str | None = None
    evaluated_at: datetime = Field(default_factory=_utcnow)
    agent_version: str | None = None
    run_ids: list[str] = Field(default_factory=list)


class EvaluationRunEnvelope(BaseModel):
    """Portable evidence envelope for one evaluation profile execution."""

    schema_version: str = "1.0"
    suite: str
    profile: str
    agent_version: str
    prompt_version: str | None = None
    model_identifier: str | None = None
    baseline_identifier: str | None = None
    test_case_ids: list[str]
    run_ids: list[str]
    evaluations: list[EvaluationResult]
    gate: GateResult
    artifact_paths: list[str] = Field(default_factory=list)
    started_at: datetime
    completed_at: datetime
