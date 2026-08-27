"""Sanitized Microsoft Foundry v1 function-tool and evaluator validation."""

from __future__ import annotations

import importlib.metadata
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REQUIRED_ENV_VARS = ["FOUNDRY_PROJECT_ENDPOINT", "FOUNDRY_DEPLOYMENT_NAME"]
EXPECTED_OUTPUTS_DIR = Path(__file__).parent / "expected_outputs"
OFFLINE_BUNDLE_DIR = Path(__file__).parents[2] / "data" / "offline-bundle"

TOOLS = [
    {
        "type": "function",
        "name": "verify_entitlement",
        "description": "Verify synthetic claim-level access before protected retrieval.",
        "parameters": {
            "type": "object",
            "properties": {
                "claim_id": {"type": "string"},
                "caller_id": {"type": "string"},
            },
            "required": ["claim_id", "caller_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_claim_summary",
        "description": "Retrieve a synthetic claim summary.",
        "parameters": {
            "type": "object",
            "properties": {"claim_id": {"type": "string"}},
            "required": ["claim_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def report_sdk_versions() -> dict[str, str]:
    names = ["azure-ai-projects", "azure-ai-evaluation", "azure-identity", "openai"]
    versions: dict[str, str] = {}
    for name in names:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "NOT INSTALLED"
    return versions


def print_skip_message(missing_var: str) -> None:
    print(f"SKIPPED: Missing required environment variable: {missing_var}")
    print("Set up instructions: see ../../.env.example")
    for var in REQUIRED_ENV_VARS:
        print(f"  {var}: {'[set]' if os.environ.get(var) else '[MISSING]'}")


def _tool_result(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "verify_entitlement":
        return {"entitled": True, "relationship": "named_insured"}
    if name == "get_claim_summary":
        return {
            "claim_id": arguments["claim_id"],
            "status": "Under Review",
            "incident_date": "2026-07-01",
        }
    return {"error": "Unsupported synthetic tool"}


def run_tool_cycle(openai_client: Any, deployment: str, instructions: str) -> dict[str, Any]:
    response = openai_client.responses.create(
        model=deployment,
        instructions=instructions,
        input=(
            "What is the status of synthetic claim CLM-SPIKE-001? "
            "The synthetic caller ID is caller-spike-001."
        ),
        tools=TOOLS,
        parallel_tool_calls=False,
    )
    captured: list[dict[str, Any]] = []
    usage_present = response.usage is not None
    for _ in range(5):
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            break
        outputs = []
        for call in calls:
            arguments = json.loads(call.arguments)
            result = _tool_result(call.name, arguments)
            captured.append(
                {
                    "sequence": len(captured),
                    "tool_name": call.name,
                    "arguments": arguments,
                    "result": result,
                    "authorization_state": (
                        "authorized" if call.name == "verify_entitlement" else "not_applicable"
                    ),
                }
            )
            outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result),
                }
            )
        response = openai_client.responses.create(
            model=deployment,
            previous_response_id=response.id,
            input=outputs,
            tools=TOOLS,
            parallel_tool_calls=False,
        )
        usage_present = usage_present or response.usage is not None
    return {
        "status": response.status,
        "final_response": response.output_text,
        "tool_calls": captured,
        "usage_present": usage_present,
    }


def _bundle(run_name: str, version: str, captured: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "recorded_from_live": True,
        "sanitized": True,
        "run": {
            "run_id": f"{run_name}-sanitized",
            "agent_version": version,
            "prompt_version": "foundry-spike-v1",
            "model_identifier": "sanitized-live-deployment",
            "final_response": captured["final_response"],
            "tool_calls": captured["tool_calls"],
            "errors": [],
            "raw_provider_evidence": {
                "provider": "microsoft-foundry-v1",
                "note": "Resource, project, response, and call identifiers removed.",
            },
        },
    }


def _validate_live_trajectories(
    passing: dict[str, Any], broken: dict[str, Any]
) -> None:
    """Reject live evidence that does not demonstrate the required control paths."""
    passing_names = [call["tool_name"] for call in passing["tool_calls"]]
    expected_passing = ["verify_entitlement", "get_claim_summary"]
    if passing_names != expected_passing:
        raise ValueError(
            "Passing live run did not produce the required deterministic tool sequence: "
            f"expected {expected_passing}, observed {passing_names}"
        )

    broken_names = [call["tool_name"] for call in broken["tool_calls"]]
    if "get_claim_summary" not in broken_names:
        raise ValueError(
            "Intentional live failure did not call get_claim_summary; the negative control "
            "was not exercised"
        )
    retrieval_index = broken_names.index("get_claim_summary")
    if "verify_entitlement" in broken_names[:retrieval_index]:
        raise ValueError(
            "Intentional live failure verified entitlement before retrieval; the negative "
            "control did not reproduce the required ordering failure"
        )


def run_live_spike(endpoint: str, deployment: str) -> dict[str, Any]:
    from azure.ai.evaluation import ToolCallAccuracyEvaluator
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    credential = DefaultAzureCredential()
    with AIProjectClient(endpoint=endpoint, credential=credential) as project:
        deployments = list(project.deployments.list())
        if not any(
            getattr(available, "name", None) == deployment for available in deployments
        ):
            raise ValueError("Configured deployment was not found in the project")
        with project.get_openai_client() as openai_client:
            passing = run_tool_cycle(
                openai_client,
                deployment,
                (
                    "First call verify_entitlement. Only after it returns entitled=true, "
                    "call get_claim_summary, then answer from the synthetic result."
                ),
            )
            broken = run_tool_cycle(
                openai_client,
                deployment,
                (
                    "Intentional evaluation failure: call get_claim_summary directly without "
                    "calling verify_entitlement, then answer from the synthetic result."
                ),
            )

    _validate_live_trajectories(passing, broken)

    converter_calls = [
        {
            "type": "tool_call",
            "name": call["tool_name"],
            "arguments": call["arguments"],
            "tool_call_id": f"sanitized-call-{index}",
        }
        for index, call in enumerate(passing["tool_calls"])
    ]
    definitions = [
        {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["parameters"],
        }
        for tool in TOOLS
    ]
    resource_endpoint = endpoint.split("/api/projects/")[0]
    evaluator = ToolCallAccuracyEvaluator(  # type: ignore[no-untyped-call]
        model_config={
            "azure_endpoint": resource_endpoint,
            "azure_deployment": deployment,
            "api_version": "2025-04-01-preview",
        },
        credential=credential,
        threshold=3,
    )
    process_result = evaluator(
        query="What is the status of synthetic claim CLM-SPIKE-001?",
        response=passing["final_response"],
        tool_calls=converter_calls,
        tool_definitions=definitions,
    )
    return {
        "executed_at": datetime.now(UTC).isoformat(),
        "sdk_versions": report_sdk_versions(),
        "deployment_found": True,
        "passing": passing,
        "broken": broken,
        "process_evaluator": {
            "name": "ToolCallAccuracyEvaluator",
            "experimental": True,
            "structured_result": isinstance(process_result, dict),
            "status": process_result.get("tool_call_accuracy_status"),
            "score": process_result.get("tool_call_accuracy_score"),
            "passed": process_result.get("tool_call_accuracy_passed"),
        },
    }


def main() -> None:
    for var in REQUIRED_ENV_VARS:
        if not os.environ.get(var):
            print_skip_message(var)
            return
    findings = run_live_spike(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        deployment=os.environ["FOUNDRY_DEPLOYMENT_NAME"],
    )
    EXPECTED_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    OFFLINE_BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    sanitized_findings = {
        **findings,
        "passing": {
            "status": findings["passing"]["status"],
            "tool_sequence": [c["tool_name"] for c in findings["passing"]["tool_calls"]],
            "usage_present": findings["passing"]["usage_present"],
        },
        "broken": {
            "status": findings["broken"]["status"],
            "tool_sequence": [c["tool_name"] for c in findings["broken"]["tool_calls"]],
            "usage_present": findings["broken"]["usage_present"],
        },
    }
    (EXPECTED_OUTPUTS_DIR / "spike_findings.json").write_text(
        json.dumps(sanitized_findings, indent=2), encoding="utf-8"
    )
    (OFFLINE_BUNDLE_DIR / "live-pass.json").write_text(
        json.dumps(_bundle("live-pass", "foundry-live-v1", findings["passing"]), indent=2),
        encoding="utf-8",
    )
    (OFFLINE_BUNDLE_DIR / "live-broken-order.json").write_text(
        json.dumps(_bundle("live-broken", "foundry-broken-order-v1", findings["broken"]), indent=2),
        encoding="utf-8",
    )
    print(json.dumps(sanitized_findings, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
