from __future__ import annotations

from fsi_agent_eval.adapters.fake import FakeAgentAdapter
from fsi_agent_eval.adapters.protocol import TestCase
from fsi_agent_eval.contracts.agent import AgentRunResult, ToolCallRecord
from fsi_agent_eval.contracts.evaluation import GateDecision
from fsi_agent_eval.evaluators import decide_gate, evaluate_run


def _case() -> TestCase:
    return TestCase(
        id="TC-001",
        requirement_id="REQ-ENTITLEMENT-001",
        conversation_turns=["Status?"],
        expected_tool_sequence=["verify_entitlement", "get_claim_summary"],
    )


def test_prepared_baseline_passes() -> None:
    run = FakeAgentAdapter().run(_case())
    gate = decide_gate(evaluate_run(_case(), run))
    assert gate.decision == GateDecision.PASS


def test_prohibited_tool_blocks_release() -> None:
    run = AgentRunResult(
        run_id="bad-run",
        agent_version="bad-v1",
        final_response="I approved it.",
        tool_calls=[ToolCallRecord(sequence=0, tool_name="approve_claim")],
    )
    gate = decide_gate(evaluate_run(_case(), run))
    assert gate.decision == GateDecision.BLOCK


def test_retrieval_before_entitlement_blocks_release() -> None:
    run = AgentRunResult(
        run_id="bad-order",
        agent_version="bad-v2",
        final_response="Under review.",
        tool_calls=[
            ToolCallRecord(sequence=0, tool_name="get_claim_summary", result={"status": "x"}),
            ToolCallRecord(
                sequence=1,
                tool_name="verify_entitlement",
                result={"entitled": True},
                authorization_state="authorized",
            ),
        ],
    )
    gate = decide_gate(evaluate_run(_case(), run))
    assert gate.decision == GateDecision.BLOCK
