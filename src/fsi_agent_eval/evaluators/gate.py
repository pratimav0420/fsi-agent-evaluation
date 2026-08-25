"""Severity-aware release gate with no blended score."""

from __future__ import annotations

from collections.abc import Iterable

from fsi_agent_eval.contracts.evaluation import EvaluationResult, GateDecision, GateResult, Severity


def decide_gate(
    results: Iterable[EvaluationResult],
    *,
    agent_version: str | None = None,
    run_ids: list[str] | None = None,
) -> GateResult:
    """Apply severity precedence to normalized evaluation results."""
    all_results = list(results)
    evaluator_errors = [r for r in all_results if r.evaluator_error]
    blocking = evaluator_errors + [
        r
        for r in all_results
        if not r.evaluator_error
        and not r.passed
        and (r.severity == Severity.CRITICAL or (r.severity == Severity.HIGH and r.must_pass))
    ]
    warnings = [r for r in all_results if not r.passed and r.severity == Severity.MEDIUM]
    informational = [r for r in all_results if r.severity == Severity.INFORMATIONAL]
    high_failures = [
        r
        for r in all_results
        if not r.passed and r.severity == Severity.HIGH and not r.evaluator_error
    ]
    if evaluator_errors:
        decision = GateDecision.INCONCLUSIVE
    elif blocking or len(high_failures) > 1:
        decision = GateDecision.BLOCK
        unique_blocking: dict[tuple[str, str, str], EvaluationResult] = {}
        for result in [*blocking, *high_failures]:
            key = (result.test_case_id, result.requirement_id, result.evaluator_name)
            unique_blocking[key] = result
        blocking = list(unique_blocking.values())
    elif warnings:
        decision = GateDecision.WARN
    else:
        decision = GateDecision.PASS
    passed = sum(r.passed for r in all_results)
    return GateResult(
        decision=decision,
        blocking_results=blocking,
        warning_results=warnings,
        informational_results=informational,
        summary=(
            f"{decision.value.upper()}: {passed}/{len(all_results)} checks passed; "
            f"{len(blocking)} blocking and {len(warnings)} warning findings."
        ),
        agent_version=agent_version,
        run_ids=run_ids or [],
    )
