"""Validated requirement and dataset specifications."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, model_validator

from fsi_agent_eval.adapters.protocol import TestCase
from fsi_agent_eval.contracts.evaluation import Severity


class RequirementSpec(BaseModel):
    id: str
    title: str
    normative_statement: str
    rationale: str
    domain: str
    severity: Severity
    owner: str
    lifecycle_stage: str
    observable_behavior: list[str]
    positive_conditions: list[str]
    negative_conditions: list[str]
    evaluator_methods: list[str]
    gate_policy: str
    evidence: list[str]
    limitations: list[str]


class CaseOracle(BaseModel):
    methods: list[str]
    expected_response_contains: list[str] = Field(default_factory=list)


class CaseSpec(BaseModel):
    id: str
    category: Literal[
        "happy_path",
        "boundary_ambiguity",
        "prohibited_adversarial",
        "operational_failure",
        "cross_customer_authorization",
    ]
    requirement_ids: list[str]
    severity: Severity
    conversation_turns: list[str]
    persona: str
    entitlement: Literal["authorized", "denied", "unknown"]
    intent: str
    claim_id: str
    caller_id: str
    expected_outcome: str
    expected_tools: list[str]
    prohibited_tools: list[str]
    escalation_expected: bool
    oracle: CaseOracle
    retained_evidence: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_traceability(self) -> CaseSpec:
        if not self.requirement_ids:
            raise ValueError("Every case must link at least one requirement")
        if not self.oracle.methods:
            raise ValueError("Every case must define at least one evaluator/oracle")
        return self


class CatalogValidation(BaseModel):
    requirement_count: int
    case_count: int
    traceability_coverage: float
    category_counts: dict[str, int]


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_catalog(requirements_path: Path, cases_path: Path) -> CatalogValidation:
    requirements = [RequirementSpec.model_validate(item) for item in load_yaml(requirements_path)]
    cases = [CaseSpec.model_validate(item) for item in load_yaml(cases_path)]
    requirement_ids = {requirement.id for requirement in requirements}
    if len(requirement_ids) != len(requirements):
        raise ValueError("Requirement IDs must be unique")
    case_ids = {case.id for case in cases}
    if len(case_ids) != len(cases):
        raise ValueError("Case IDs must be unique")
    unknown = sorted({rid for case in cases for rid in case.requirement_ids} - requirement_ids)
    if unknown:
        raise ValueError(f"Cases reference unknown requirements: {unknown}")
    category_counts: dict[str, int] = {}
    for case in cases:
        category_counts[case.category] = category_counts.get(case.category, 0) + 1
    expected = {
        "happy_path": 5,
        "boundary_ambiguity": 5,
        "prohibited_adversarial": 5,
        "operational_failure": 3,
        "cross_customer_authorization": 2,
    }
    if len(cases) != 20 or category_counts != expected:
        raise ValueError(f"Dataset distribution must be exactly {expected}; got {category_counts}")
    return CatalogValidation(
        requirement_count=len(requirements),
        case_count=len(cases),
        traceability_coverage=1.0,
        category_counts=category_counts,
    )


def load_test_cases(path: Path) -> list[TestCase]:
    """Load validated YAML cases into the provider-neutral adapter contract."""
    cases = [CaseSpec.model_validate(item) for item in load_yaml(path)]
    return [
        TestCase(
            id=case.id,
            requirement_id=case.requirement_ids[0],
            requirement_ids=case.requirement_ids[1:],
            conversation_turns=case.conversation_turns,
            expected_tool_sequence=case.expected_tools,
            metadata={
                **case.metadata,
                "category": case.category,
                "severity": case.severity.value,
                "intent": case.intent,
                "claim_id": case.claim_id,
                "caller_id": case.caller_id,
                "entitlement": case.entitlement,
                "expected_outcome": case.expected_outcome,
                "prohibited_tools": case.prohibited_tools,
                "escalation_expected": case.escalation_expected,
                "expected_response_contains": case.oracle.expected_response_contains,
                "must_pass": case.severity in {Severity.CRITICAL, Severity.HIGH},
            },
        )
        for case in cases
    ]
