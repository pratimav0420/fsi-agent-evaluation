"""Deterministic local claims agent used by the offline evaluation demo."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from time import sleep
from uuid import uuid4

from fsi_agent_eval.adapters.protocol import TestCase
from fsi_agent_eval.contracts.agent import AgentRunResult, ToolCallRecord
from fsi_agent_eval.tools.claims import (
    create_human_escalation,
    get_claim_summary,
    get_required_documents,
    verify_entitlement,
)


class LocalAgentAdapter:
    """Scenario-aware, deterministic implementation of the agent contract."""

    def __init__(self, agent_version: str = "local-v0.2.0") -> None:
        self._agent_version = agent_version

    def run(self, test_case: TestCase) -> AgentRunResult:
        metadata = test_case.metadata
        claim_id = str(metadata.get("claim_id", "CLM-FAKE-20260101-001"))
        caller_id = str(metadata.get("caller_id", "caller-001"))
        intent = str(metadata.get("intent", "status"))
        started = datetime.now(UTC)
        calls: list[ToolCallRecord] = []

        latency_ms = int(metadata.get("simulate_latency_ms", 0))
        if latency_ms:
            sleep(latency_ms / 1000)

        entitlement = verify_entitlement(claim_id, caller_id)
        calls.append(
            self._call(
                0,
                "verify_entitlement",
                {"claim_id": claim_id, "caller_id": caller_id},
                entitlement,
                started,
                "authorized" if entitlement["entitled"] else "denied",
            )
        )

        if not entitlement["entitled"]:
            response = (
                "I cannot access that claim for this caller. "
                "I can help create a human review request."
            )
        elif intent in {"prohibited_decision", "ambiguous"}:
            reason = "Request requires an authorized claims professional."
            escalation = create_human_escalation(claim_id, reason)
            calls.append(
                self._call(
                    1,
                    "create_human_escalation",
                    {"claim_id": claim_id, "reason": reason},
                    escalation,
                    started + timedelta(milliseconds=10),
                    "authorized",
                )
            )
            response = "I cannot make or change a claim decision. I created a human review request."
        elif intent == "documents":
            documents = get_required_documents(claim_id)
            calls.append(
                self._call(
                    1,
                    "get_required_documents",
                    {"claim_id": claim_id},
                    documents,
                    started + timedelta(milliseconds=10),
                    "authorized",
                )
            )
            names = ", ".join(documents.get("required_documents", []))
            response = f"The required documents are: {names}."
        else:
            if metadata.get("simulate_tool_error"):
                calls.append(
                    ToolCallRecord(
                        sequence=1,
                        tool_name="get_claim_summary",
                        arguments={"claim_id": claim_id},
                        error="Synthetic claim service unavailable",
                        start_time=started + timedelta(milliseconds=10),
                        end_time=started + timedelta(milliseconds=15),
                        authorization_state="authorized",
                    )
                )
                response = "I cannot retrieve the claim right now and will not guess its status."
            else:
                summary = get_claim_summary(claim_id)
                calls.append(
                    self._call(
                        1,
                        "get_claim_summary",
                        {"claim_id": claim_id},
                        summary,
                        started + timedelta(milliseconds=10),
                        "authorized",
                    )
                )
                response = f"Claim {claim_id} is currently {summary.get('status', 'unavailable')}."

        return AgentRunResult(
            run_id=f"run-{uuid4().hex[:12]}",
            agent_version=self._agent_version,
            prompt_version="offline-prompt-v2",
            model_identifier="deterministic-local",
            final_response=response,
            tool_calls=calls,
            start_time=started,
            end_time=datetime.now(UTC),
            raw_provider_evidence={"provider": "local", "synthetic": True},
        )

    @staticmethod
    def _call(
        sequence: int,
        name: str,
        arguments: dict[str, str],
        result: dict[str, object],
        started: datetime,
        authorization_state: str,
    ) -> ToolCallRecord:
        return ToolCallRecord(
            sequence=sequence,
            tool_name=name,
            arguments=arguments,
            result=result,
            start_time=started,
            end_time=started + timedelta(milliseconds=5),
            authorization_state=authorization_state,
        )


class BrokenOrderingAdapter(LocalAgentAdapter):
    """Intentional failure: retrieves claim data before checking entitlement."""

    def __init__(self) -> None:
        super().__init__(agent_version="broken-ordering-v0.2.0")

    def run(self, test_case: TestCase) -> AgentRunResult:
        result = super().run(test_case)
        retrieval = [
            call
            for call in result.tool_calls
            if call.tool_name in {"get_claim_summary", "get_required_documents"}
        ]
        entitlement = [call for call in result.tool_calls if call.tool_name == "verify_entitlement"]
        others = [
            call for call in result.tool_calls if call not in retrieval and call not in entitlement
        ]
        result.tool_calls = retrieval + entitlement + others
        for sequence, call in enumerate(result.tool_calls):
            call.sequence = sequence
        return result
