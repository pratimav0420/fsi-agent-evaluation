from fsi_agent_eval.contracts.evaluation import EvaluationResult, GateDecision, Severity
from fsi_agent_eval.evaluators.gate import decide_gate


def _result(
    *, passed: bool, severity: Severity, must_pass: bool = False, error: str | None = None
) -> EvaluationResult:
    return EvaluationResult(
        evaluator_name="test",
        requirement_id="FSI-REL-001",
        test_case_id="case",
        passed=passed,
        severity=severity,
        must_pass=must_pass,
        evaluator_error=error,
    )


def test_evaluator_error_is_inconclusive() -> None:
    gate = decide_gate([_result(passed=False, severity=Severity.HIGH, error="judge unavailable")])
    assert gate.decision == GateDecision.INCONCLUSIVE


def test_critical_failure_blocks() -> None:
    gate = decide_gate([_result(passed=False, severity=Severity.CRITICAL)])
    assert gate.decision == GateDecision.BLOCK


def test_single_non_must_pass_high_does_not_block() -> None:
    gate = decide_gate([_result(passed=False, severity=Severity.HIGH)])
    assert gate.decision == GateDecision.PASS


def test_high_must_pass_blocks() -> None:
    gate = decide_gate([_result(passed=False, severity=Severity.HIGH, must_pass=True)])
    assert gate.decision == GateDecision.BLOCK
