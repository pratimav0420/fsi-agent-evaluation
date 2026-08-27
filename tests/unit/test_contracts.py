"""Unit tests for contract serialization and normalization."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from fsi_agent_eval.contracts.agent import AgentRunResult, TokenUsage, ToolCallRecord
from fsi_agent_eval.contracts.evaluation import (
    EvaluationResult,
    GateDecision,
    GateResult,
    Severity,
)
from fsi_agent_eval.contracts.trace import NormalizedTrace, RawToolCallTrace


class TestToolCallRecordSerialization:
    """Contract serialization round-trip tests for ToolCallRecord."""

    def test_round_trip_full(self) -> None:
        record = ToolCallRecord(
            sequence=0,
            tool_name="get_claim_summary",
            arguments={"claim_id": "CLM-001"},
            result={"status": "Under Review"},
            start_time=datetime(2026, 8, 7, 10, 0, 0, tzinfo=UTC),
            end_time=datetime(2026, 8, 7, 10, 0, 1, tzinfo=UTC),
            authorization_state="authorized",
        )
        serialized = record.model_dump_json()
        deserialized = ToolCallRecord.model_validate_json(serialized)
        assert deserialized == record

    def test_round_trip_minimal(self) -> None:
        """Optional fields can be None and still round-trip."""
        record = ToolCallRecord(
            sequence=0,
            tool_name="verify_entitlement",
            arguments={"claim_id": "CLM-001", "caller_id": "caller-1"},
        )
        serialized = record.model_dump_json()
        deserialized = ToolCallRecord.model_validate_json(serialized)
        assert deserialized.result is None
        assert deserialized.error is None
        assert deserialized.start_time is None
        assert deserialized.end_time is None
        assert deserialized.authorization_state is None

    def test_error_tool_call(self) -> None:
        """A tool call with an error and no result is valid."""
        record = ToolCallRecord(
            sequence=2,
            tool_name="get_claim_summary",
            arguments={"claim_id": "NONEXISTENT"},
            error="Claim not found",
        )
        serialized = record.model_dump_json()
        deserialized = ToolCallRecord.model_validate_json(serialized)
        assert deserialized.result is None
        assert deserialized.error == "Claim not found"


class TestAgentRunResultSerialization:
    """Contract serialization round-trip tests for AgentRunResult."""

    def test_round_trip(self) -> None:
        result = AgentRunResult(
            run_id="run-001",
            agent_version="v0.1.0",
            prompt_version="prompt-v1",
            model_identifier="synthetic-test-deployment",
            final_response="Your claim is under review.",
            tool_calls=[
                ToolCallRecord(
                    sequence=0,
                    tool_name="get_claim_summary",
                    arguments={"claim_id": "CLM-001"},
                    result={"status": "Under Review"},
                ),
            ],
            token_usage=TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
        )
        serialized = result.model_dump_json()
        deserialized = AgentRunResult.model_validate_json(serialized)
        assert deserialized.run_id == "run-001"
        assert len(deserialized.tool_calls) == 1
        assert deserialized.tool_calls[0].tool_name == "get_claim_summary"

    def test_missing_optional_telemetry(self) -> None:
        """Handles missing optional telemetry safely."""
        result = AgentRunResult(
            run_id="run-002",
            agent_version="v0.1.0",
            final_response="No data available.",
        )
        assert result.token_usage is None
        assert result.model_identifier is None
        assert result.prompt_version is None
        assert result.start_time is None
        assert result.end_time is None
        assert result.tool_calls == []
        assert result.errors == []

    def test_json_file_output(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        """Results can be written to JSON file (evidence retention)."""
        result = AgentRunResult(
            run_id="run-003",
            agent_version="v0.1.0",
            final_response="Test.",
            tool_calls=[
                ToolCallRecord(sequence=0, tool_name="verify_entitlement", arguments={}),
            ],
        )
        output_path = tmp_path / "result.json"
        output_path.write_text(result.model_dump_json(indent=2))
        loaded = json.loads(output_path.read_text())
        assert loaded["run_id"] == "run-003"


class TestTraceContracts:
    """Tests for trace normalization contracts."""

    def test_raw_trace_round_trip(self) -> None:
        trace = RawToolCallTrace(
            provider_call_id="call_abc123",
            tool_name="get_claim_summary",
            arguments_raw='{"claim_id": "CLM-001"}',
            output_raw='{"status": "Under Review"}',
            step_id="step_xyz",
            step_created_at=datetime(2026, 8, 7, 10, 0, 0, tzinfo=UTC),
            step_completed_at=datetime(2026, 8, 7, 10, 0, 1, tzinfo=UTC),
        )
        serialized = trace.model_dump_json()
        deserialized = RawToolCallTrace.model_validate_json(serialized)
        assert deserialized.provider_call_id == "call_abc123"
        assert deserialized.output_raw == '{"status": "Under Review"}'

    def test_normalized_trace_round_trip(self) -> None:
        trace = NormalizedTrace(
            run_id="run-001",
            thread_id="thread-001",
            model="synthetic-test-deployment",
            tool_call_traces=[
                RawToolCallTrace(
                    provider_call_id="call_1",
                    tool_name="verify_entitlement",
                    arguments_raw='{"claim_id": "CLM-001", "caller_id": "c-1"}',
                ),
            ],
            prompt_tokens=200,
            completion_tokens=50,
            total_tokens=250,
        )
        serialized = trace.model_dump_json()
        deserialized = NormalizedTrace.model_validate_json(serialized)
        assert len(deserialized.tool_call_traces) == 1


class TestEvaluationContracts:
    """Tests for evaluation result contracts."""

    def test_evaluation_result_round_trip(self) -> None:
        result = EvaluationResult(
            evaluator_name="entitlement_before_retrieval",
            requirement_id="FSI-AUTH-001",
            test_case_id="FSI-CASE-001",
            passed=True,
            severity=Severity.CRITICAL,
            message="verify_entitlement called before get_claim_summary",
        )
        serialized = result.model_dump_json()
        deserialized = EvaluationResult.model_validate_json(serialized)
        assert deserialized.severity == Severity.CRITICAL
        assert deserialized.passed is True

    def test_gate_result_blocking(self) -> None:
        failed = EvaluationResult(
            evaluator_name="prohibited_tool_check",
            requirement_id="FSI-ACT-001",
            test_case_id="FSI-CASE-005",
            passed=False,
            severity=Severity.CRITICAL,
            message="Agent called modify_claim which is prohibited.",
        )
        gate = GateResult(
            decision=GateDecision.BLOCK,
            blocking_results=[failed],
            agent_version="v0.1.0",
        )
        assert gate.decision == GateDecision.BLOCK
        assert len(gate.blocking_results) == 1
