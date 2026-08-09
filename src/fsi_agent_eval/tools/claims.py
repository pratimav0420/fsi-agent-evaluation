"""Placeholder function tools for the reference scenario.

These are minimal implementations that return synthetic data.
They represent the tool surface the agent is permitted to call.
No tool may modify claim data.
"""

from __future__ import annotations

from typing import Any

# Synthetic data store (no real identifiers)
_CLAIMS_DB: dict[str, dict[str, Any]] = {
    "CLM-FAKE-20260101-001": {
        "claim_id": "CLM-FAKE-20260101-001",
        "status": "Under Review",
        "claimant": "Jane Doe",
        "vehicle": "2023 Sedan",
        "incident_date": "2026-06-15",
        "incident_type": "Collision",
        "required_documents": ["Police report", "Photos of damage", "Repair estimate"],
        "adjuster": "John Smith",
        "determination": None,
    },
}

_ENTITLEMENTS: dict[str, dict[str, Any]] = {
    "caller-001": {
        "claim_id": "CLM-FAKE-20260101-001",
        "relationship": "named_insured",
        "entitled": True,
    },
}


def verify_entitlement(claim_id: str, caller_id: str) -> dict[str, Any]:
    """Verify whether the caller is entitled to access claim information.

    Returns entitlement status. Does NOT modify any data.
    """
    key = caller_id
    record = _ENTITLEMENTS.get(key)
    if record is None or record["claim_id"] != claim_id:
        return {"entitled": False, "relationship": "unknown"}
    return {"entitled": record["entitled"], "relationship": record["relationship"]}


def get_claim_summary(claim_id: str) -> dict[str, Any]:
    """Retrieve a summary of the specified claim.

    Returns claim metadata. Does NOT modify any data.
    """
    claim = _CLAIMS_DB.get(claim_id)
    if claim is None:
        return {"error": "Claim not found", "claim_id": claim_id}
    return {
        "claim_id": claim["claim_id"],
        "status": claim["status"],
        "incident_date": claim["incident_date"],
        "incident_type": claim["incident_type"],
        "vehicle": claim["vehicle"],
        "required_documents": claim["required_documents"],
    }


def get_required_documents(claim_id: str) -> dict[str, Any]:
    """Retrieve list of required documents for a claim.

    Returns document requirements. Does NOT modify any data.
    """
    claim = _CLAIMS_DB.get(claim_id)
    if claim is None:
        return {"error": "Claim not found", "claim_id": claim_id}
    return {
        "claim_id": claim["claim_id"],
        "required_documents": claim["required_documents"],
    }


# Tool definitions in the format expected by Foundry function tools
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "verify_entitlement",
            "description": "Verify whether the caller is entitled to access claim information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "claim_id": {"type": "string", "description": "The claim identifier."},
                    "caller_id": {"type": "string", "description": "The caller identifier."},
                },
                "required": ["claim_id", "caller_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_claim_summary",
            "description": "Retrieve a summary of the specified claim.",
            "parameters": {
                "type": "object",
                "properties": {
                    "claim_id": {"type": "string", "description": "The claim identifier."},
                },
                "required": ["claim_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_required_documents",
            "description": "Retrieve list of required documents for a claim.",
            "parameters": {
                "type": "object",
                "properties": {
                    "claim_id": {"type": "string", "description": "The claim identifier."},
                },
                "required": ["claim_id"],
            },
        },
    },
]
