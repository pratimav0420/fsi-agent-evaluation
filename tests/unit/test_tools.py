from fsi_agent_eval.tools.claims import (
    create_human_escalation,
    get_claim_summary,
    get_required_documents,
    verify_entitlement,
)


def test_entitlement_is_claim_specific() -> None:
    assert verify_entitlement("CLM-FAKE-20260101-001", "caller-001")["entitled"] is True
    assert verify_entitlement("CLM-FAKE-20260202-002", "caller-001")["entitled"] is False


def test_missing_claim_is_explicit() -> None:
    assert "error" in get_claim_summary("CLM-MISSING")
    assert "error" in get_required_documents("CLM-MISSING")


def test_escalation_uses_synthetic_identifier() -> None:
    result = create_human_escalation("CLM-FAKE-20260101-001", "Human review requested")
    assert result["escalation_id"].startswith("ESC-FAKE-")
    assert result["status"] == "queued"
