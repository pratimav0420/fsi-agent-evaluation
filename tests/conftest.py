"""Test fixtures for FSI Agent Evaluation tests."""

from __future__ import annotations

import pytest

from fsi_agent_eval.adapters.fake import FakeAgentAdapter
from fsi_agent_eval.adapters.protocol import TestCase


@pytest.fixture
def fake_adapter() -> FakeAgentAdapter:
    """Provide a fake adapter instance."""
    return FakeAgentAdapter()


@pytest.fixture
def sample_test_case() -> TestCase:
    """Provide a sample test case for the claims scenario."""
    return TestCase(
        id="TC-001",
        requirement_id="FSI-AUTH-001",
        conversation_turns=["What is the status of my claim CLM-FAKE-20260101-001?"],
        expected_tool_sequence=["verify_entitlement", "get_claim_summary"],
    )
