"""Provider-neutral contracts for semantic evaluators."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, Field

from fsi_agent_eval.adapters.protocol import TestCase
from fsi_agent_eval.contracts.agent import AgentRunResult
from fsi_agent_eval.contracts.evaluation import EvaluationResult


class SemanticRubric(BaseModel):
    name: str
    requirement_id: str
    criteria: list[str]
    pass_threshold: float = Field(ge=0, le=1)


class SemanticEvaluator(Protocol):
    """Interface for Foundry or recorded semantic judges."""

    def evaluate(
        self, rubric: SemanticRubric, test_case: TestCase, run: AgentRunResult
    ) -> EvaluationResult: ...


class RecordedSemanticEvaluator:
    """Replay reviewed semantic results in the credential-free offline demo."""

    def __init__(self, results: dict[tuple[str, str], EvaluationResult]) -> None:
        self._results = results

    def evaluate(
        self, rubric: SemanticRubric, test_case: TestCase, run: AgentRunResult
    ) -> EvaluationResult:
        del run
        key = (rubric.name, test_case.id)
        if key not in self._results:
            raise KeyError(f"No reviewed semantic result for {key}")
        return self._results[key].model_copy(deep=True)
