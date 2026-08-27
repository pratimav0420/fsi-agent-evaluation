"""Fake agent adapter for offline testing.

This adapter produces realistic normalized traces without requiring Azure
credentials. It is test infrastructure, not the final sample agent.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fsi_agent_eval.adapters.protocol import AgentAdapter, TestCase
from fsi_agent_eval.contracts.agent import AgentRunResult, TokenUsage, ToolCallRecord

# Synthetic claim data (no real policy or claim identifiers)
_SYNTHETIC_CLAIM = {
    "claim_id": "CLM-FAKE-20260101-001",
    "status": "Under Review",
    "claimant": "Jane Doe",
    "vehicle": "2023 Sedan",
    "incident_date": "2026-06-15",
    "required_documents": ["Police report", "Photos of damage", "Repair estimate"],
    "adjuster": "John Smith",
    "determination": None,
}


class FakeAgentAdapter:
    """Produces a deterministic normalized trace for testing.

    Simulates a post-FNOL claims servicing agent that:
    1. Verifies entitlement
    2. Retrieves claim status
    3. Returns a response summarizing the claim

    This is intentionally minimal — just enough to validate contracts and
    evaluator plumbing.
    """

    def __init__(self, agent_version: str = "fake-v0.1.0") -> None:
        self._agent_version = agent_version

    def run(self, test_case: TestCase) -> AgentRunResult:
        """Return a pre-built normalized trace."""
        base_time = datetime(2026, 8, 7, 10, 0, 0, tzinfo=UTC)

        tool_calls = [
            ToolCallRecord(
                sequence=0,
                tool_name="verify_entitlement",
                arguments={"claim_id": "CLM-FAKE-20260101-001", "caller_id": "caller-001"},
                result={"entitled": True, "relationship": "named_insured"},
                start_time=base_time,
                end_time=base_time.replace(second=1),
                authorization_state="authorized",
            ),
            ToolCallRecord(
                sequence=1,
                tool_name="get_claim_summary",
                arguments={"claim_id": "CLM-FAKE-20260101-001"},
                result={
                    "claim_id": _SYNTHETIC_CLAIM["claim_id"],
                    "status": _SYNTHETIC_CLAIM["status"],
                    "incident_date": _SYNTHETIC_CLAIM["incident_date"],
                    "vehicle": _SYNTHETIC_CLAIM["vehicle"],
                    "required_documents": _SYNTHETIC_CLAIM["required_documents"],
                },
                start_time=base_time.replace(second=1),
                end_time=base_time.replace(second=2),
                authorization_state="not_applicable",
            ),
        ]

        return AgentRunResult(
            run_id="run-fake-001",
            agent_version=self._agent_version,
            prompt_version="prompt-v1",
            model_identifier="synthetic-test-deployment",
            final_response=(
                "Your claim CLM-FAKE-20260101-001 is currently Under Review. "
                "The incident on 2026-06-15 involving your 2023 Sedan is being assessed. "
                "We still need the following documents: Police report, Photos of damage, "
                "Repair estimate. Would you like me to explain what each document requires?"
            ),
            tool_calls=tool_calls,
            citations=[],
            start_time=base_time,
            end_time=base_time.replace(second=5),
            token_usage=TokenUsage(
                prompt_tokens=350,
                completion_tokens=85,
                total_tokens=435,
            ),
            errors=[],
            raw_provider_evidence={
                "_note": "This is fake diagnostic data for testing only.",
                "provider": "fake",
            },
        )


# Verify protocol compliance at import time
_adapter: AgentAdapter = FakeAgentAdapter()
