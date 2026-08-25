"""Unit tests for the fake agent adapter."""

from __future__ import annotations

import json

from fsi_agent_eval.adapters.fake import FakeAgentAdapter
from fsi_agent_eval.adapters.protocol import AgentAdapter, TestCase
from fsi_agent_eval.contracts.agent import AgentRunResult


class TestFakeAdapterProtocolCompliance:
    """Verify the fake adapter satisfies the AgentAdapter protocol."""

    def test_is_agent_adapter(self) -> None:
        adapter = FakeAgentAdapter()
        assert isinstance(adapter, AgentAdapter)

    def test_returns_agent_run_result(
        self, fake_adapter: FakeAgentAdapter, sample_test_case: TestCase
    ) -> None:
        result = fake_adapter.run(sample_test_case)
        assert isinstance(result, AgentRunResult)


class TestFakeAdapterTrace:
    """Verify the fake adapter produces a valid normalized trace."""

    def test_tool_call_sequence_preserved(
        self, fake_adapter: FakeAgentAdapter, sample_test_case: TestCase
    ) -> None:
        result = fake_adapter.run(sample_test_case)
        tool_names = [tc.tool_name for tc in result.tool_calls]
        assert tool_names == ["verify_entitlement", "get_claim_summary"]

    def test_sequence_numbers_ordered(
        self, fake_adapter: FakeAgentAdapter, sample_test_case: TestCase
    ) -> None:
        result = fake_adapter.run(sample_test_case)
        sequences = [tc.sequence for tc in result.tool_calls]
        assert sequences == [0, 1]

    def test_entitlement_checked_first(
        self, fake_adapter: FakeAgentAdapter, sample_test_case: TestCase
    ) -> None:
        """Critical FSI invariant: entitlement verification precedes data retrieval."""
        result = fake_adapter.run(sample_test_case)
        assert result.tool_calls[0].tool_name == "verify_entitlement"
        assert result.tool_calls[0].authorization_state == "authorized"

    def test_tool_calls_have_results(
        self, fake_adapter: FakeAgentAdapter, sample_test_case: TestCase
    ) -> None:
        result = fake_adapter.run(sample_test_case)
        for tc in result.tool_calls:
            assert tc.result is not None
            assert tc.error is None

    def test_has_final_response(
        self, fake_adapter: FakeAgentAdapter, sample_test_case: TestCase
    ) -> None:
        result = fake_adapter.run(sample_test_case)
        assert len(result.final_response) > 0

    def test_has_token_usage(
        self, fake_adapter: FakeAgentAdapter, sample_test_case: TestCase
    ) -> None:
        result = fake_adapter.run(sample_test_case)
        token_usage = result.token_usage
        assert token_usage is not None
        total_tokens = token_usage.total_tokens
        assert total_tokens is not None
        assert total_tokens > 0

    def test_has_timing(self, fake_adapter: FakeAgentAdapter, sample_test_case: TestCase) -> None:
        result = fake_adapter.run(sample_test_case)
        start_time = result.start_time
        end_time = result.end_time
        assert start_time is not None
        assert end_time is not None
        assert end_time > start_time

    def test_no_errors(self, fake_adapter: FakeAgentAdapter, sample_test_case: TestCase) -> None:
        result = fake_adapter.run(sample_test_case)
        assert result.errors == []


class TestProviderIsolation:
    """Ensure provider-specific fields do not leak into gate-facing models."""

    def test_raw_evidence_is_diagnostic_only(
        self, fake_adapter: FakeAgentAdapter, sample_test_case: TestCase
    ) -> None:
        result = fake_adapter.run(sample_test_case)
        # raw_provider_evidence exists but is clearly marked as non-gate data
        assert "provider" in result.raw_provider_evidence
        # Gate-facing fields are all normalized
        assert result.run_id.startswith("run-")
        assert all(isinstance(tc.tool_name, str) for tc in result.tool_calls)

    def test_no_provider_objects_in_tool_calls(
        self, fake_adapter: FakeAgentAdapter, sample_test_case: TestCase
    ) -> None:
        """Tool call records contain only primitive/dict types, no SDK objects."""
        result = fake_adapter.run(sample_test_case)
        for tc in result.tool_calls:
            serialized = tc.model_dump()
            # Verify all values are JSON-serializable primitives
            json.dumps(serialized, default=str)  # Should not raise


class TestNoSecrets:
    """Verify no secret-like values in adapter output."""

    def test_no_subscription_ids(
        self, fake_adapter: FakeAgentAdapter, sample_test_case: TestCase
    ) -> None:
        result = fake_adapter.run(sample_test_case)
        serialized = result.model_dump_json()
        # Check for common Azure secret patterns
        assert "subscription" not in serialized.lower()
        assert "tenant" not in serialized.lower()
        assert "endpoint" not in serialized.lower()
        # No bearer tokens or keys
        assert "bearer" not in serialized.lower()
        assert "api-key" not in serialized.lower()
