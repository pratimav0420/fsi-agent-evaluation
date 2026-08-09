"""Foundry Process Evaluation Spike.

This spike validates:
1. Function-tool trace serialization from azure-ai-agents
2. Trace normalization without portal dependency
3. Process evaluator compatibility
4. Structured result retrieval
5. Exact SDK versions

IMPORTANT: This is exploratory spike code, not production architecture.
Uncertain/preview APIs are isolated here and must not leak into src/.

Run: python run_spike.py
If AZURE_AI_PROJECT_CONNECTION_STRING is not set, exits with SKIPPED.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_ENV_VARS = [
    "AZURE_AI_PROJECT_CONNECTION_STRING",
    "AZURE_AI_AGENT_MODEL_DEPLOYMENT",
]

EXPECTED_OUTPUTS_DIR = Path(__file__).parent / "expected_outputs"


def check_environment() -> dict[str, str] | None:
    """Check required environment variables. Returns config dict or None if missing."""
    config = {}
    for var in REQUIRED_ENV_VARS:
        value = os.environ.get(var)
        if not value:
            return None
        config[var] = value
    return config


def print_skip_message(missing_var: str) -> None:
    """Print skip message with setup instructions."""
    print(f"SKIPPED: Missing required environment variable: {missing_var}")
    print("Set up instructions: see ../../.env.example")
    print()
    print("Required environment variables:")
    for var in REQUIRED_ENV_VARS:
        status = "[set]" if os.environ.get(var) else "[MISSING]"
        print(f"  {var}: {status}")


def report_sdk_versions() -> dict[str, str]:
    """Report installed SDK versions."""
    versions: dict[str, str] = {}
    try:
        import azure.ai.agents

        versions["azure-ai-agents"] = getattr(azure.ai.agents, "__version__", "unknown")
    except ImportError:
        versions["azure-ai-agents"] = "NOT INSTALLED"

    try:
        import azure.ai.projects

        versions["azure-ai-projects"] = getattr(azure.ai.projects, "__version__", "unknown")
    except ImportError:
        versions["azure-ai-projects"] = "NOT INSTALLED"

    try:
        import azure.ai.evaluation

        versions["azure-ai-evaluation"] = getattr(azure.ai.evaluation, "__version__", "unknown")
    except ImportError:
        versions["azure-ai-evaluation"] = "NOT INSTALLED"

    try:
        import azure.identity

        versions["azure-identity"] = getattr(azure.identity, "__version__", "unknown")
    except ImportError:
        versions["azure-identity"] = "NOT INSTALLED"

    return versions


def run_live_spike(config: dict[str, str]) -> None:
    """Execute the live Foundry validation spike.

    This function contains preview/uncertain API usage that must be
    validated. Do NOT copy this into src/ without confirmation.
    """
    # Late imports — only needed for live execution
    from azure.ai.agents import AgentsClient
    from azure.ai.agents.models import (
        FunctionTool,
        RunStepToolCallDetails,
        ThreadRun,
    )
    from azure.identity import DefaultAzureCredential

    print("\n=== LIVE SPIKE: Foundry Process Evaluation ===\n")

    # --- Step 1: Create agent with function tools ---
    print("[1/5] Creating agent with function tools...")

    credential = DefaultAzureCredential()
    client = AgentsClient(
        credential=credential,
        connection_string=config["AZURE_AI_PROJECT_CONNECTION_STRING"],
    )

    # Minimal function tool definition
    tool_definitions = [
        {
            "type": "function",
            "function": {
                "name": "get_claim_summary",
                "description": "Retrieve a summary of the specified claim. Returns synthetic data only.",
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

    functions = FunctionTool(functions=tool_definitions)

    agent = client.create_agent(
        model=config["AZURE_AI_AGENT_MODEL_DEPLOYMENT"],
        name="spike-claims-agent",
        instructions=(
            "You are a claims servicing assistant. Use the get_claim_summary tool "
            "to retrieve claim information when asked about a claim. "
            "Always call the tool before responding."
        ),
        tools=functions.definitions,
    )
    print(f"  Agent created: {agent.id}")

    # --- Step 2: Run a conversation that triggers tool use ---
    print("[2/5] Running conversation to trigger tool call...")

    thread = client.threads.create()
    client.messages.create(
        thread_id=thread.id,
        role="user",
        content="What is the status of claim CLM-SPIKE-001?",
    )

    run = client.runs.create(thread_id=thread.id, agent_id=agent.id)

    # Poll for completion, handling tool calls
    tool_outputs_captured: list[dict] = []
    import time

    while run.status in ("queued", "in_progress", "requires_action"):
        time.sleep(1)
        run = client.runs.get(thread_id=thread.id, run_id=run.id)

        if run.status == "requires_action" and run.required_action:
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            outputs = []
            for tc in tool_calls:
                # Capture what we submit (SDK doesn't store this in RunStep)
                synthetic_result = json.dumps({
                    "claim_id": "CLM-SPIKE-001",
                    "status": "Under Review",
                    "incident_date": "2026-07-01",
                    "vehicle": "2024 SUV",
                })
                outputs.append({"tool_call_id": tc.id, "output": synthetic_result})
                tool_outputs_captured.append({
                    "tool_call_id": tc.id,
                    "function_name": tc.function.name if hasattr(tc, "function") else "unknown",
                    "arguments": tc.function.arguments if hasattr(tc, "function") else "",
                    "output_submitted": synthetic_result,
                    "captured_at": datetime.now(timezone.utc).isoformat(),
                })

            client.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=outputs,
            )

    print(f"  Run completed with status: {run.status}")

    # --- Step 3: Retrieve RunSteps and examine trace structure ---
    print("[3/5] Retrieving RunSteps for trace analysis...")

    run_steps = client.run_steps.list(thread_id=thread.id, run_id=run.id)
    steps_data = []

    for step in run_steps:
        step_dict = step.as_dict()
        # Sanitize — remove any IDs that could be secrets
        sanitized = {
            "step_type": step.type,
            "status": step.status,
            "created_at": step.created_at.isoformat() if step.created_at else None,
            "completed_at": step.completed_at.isoformat() if step.completed_at else None,
            "has_usage": step.usage is not None,
        }

        if hasattr(step, "step_details") and isinstance(step.step_details, RunStepToolCallDetails):
            tool_calls_info = []
            for tc in step.step_details.tool_calls:
                tc_info = {
                    "type": tc.type,
                    "has_id": bool(tc.id),
                    "function_name": getattr(getattr(tc, "function", None), "name", None),
                    "has_arguments": bool(getattr(getattr(tc, "function", None), "arguments", None)),
                    "has_output_field": hasattr(getattr(tc, "function", None), "output"),
                }
                tool_calls_info.append(tc_info)
            sanitized["tool_calls"] = tool_calls_info

        if step.usage:
            sanitized["usage"] = {
                "prompt_tokens": step.usage.prompt_tokens,
                "completion_tokens": step.usage.completion_tokens,
                "total_tokens": step.usage.total_tokens,
            }

        steps_data.append(sanitized)

    # --- Step 4: Check ThreadRun metadata ---
    print("[4/5] Checking ThreadRun metadata...")

    run_metadata = {
        "status": run.status,
        "model": run.model,
        "has_usage": run.usage is not None,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
    }
    if run.usage:
        run_metadata["usage"] = {
            "prompt_tokens": run.usage.prompt_tokens,
            "completion_tokens": run.usage.completion_tokens,
            "total_tokens": run.usage.total_tokens,
        }

    # --- Step 5: Compile findings ---
    print("[5/5] Compiling findings...\n")

    findings = {
        "spike_executed_at": datetime.now(timezone.utc).isoformat(),
        "sdk_versions": report_sdk_versions(),
        "questions_answered": {
            "q1_tool_call_info": {
                "description": "What tool-call information is returned for a user-defined function tool?",
                "run_steps_captured": steps_data,
                "tool_outputs_captured_client_side": len(tool_outputs_captured),
                "finding": "TBD — examine steps_data above",
            },
            "q2_normalize_without_portal": {
                "description": "Can that information be normalized without portal-only trace?",
                "finding": "TBD — based on steps_data structure",
            },
            "q3_process_evaluators": {
                "description": "Which Foundry process evaluators accept the captured format?",
                "finding": "REQUIRES SEPARATE VALIDATION with azure-ai-evaluation",
            },
            "q4_structured_results": {
                "description": "Can structured evaluation results be retrieved programmatically?",
                "finding": "REQUIRES SEPARATE VALIDATION with azure-ai-evaluation",
            },
        },
        "run_metadata": run_metadata,
    }

    # Save sanitized output
    EXPECTED_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = EXPECTED_OUTPUTS_DIR / "spike_findings.json"
    output_path.write_text(json.dumps(findings, indent=2, default=str))
    print(f"Findings saved to: {output_path}")
    print(json.dumps(findings, indent=2, default=str))

    # Cleanup
    print("\nCleaning up agent...")
    client.delete_agent(agent.id)
    print("Done.")


def main() -> None:
    """Entry point for the spike."""
    print("=" * 60)
    print("Foundry Process Evaluation Spike")
    print("=" * 60)

    versions = report_sdk_versions()
    print("\nSDK Versions:")
    for pkg, ver in versions.items():
        print(f"  {pkg}: {ver}")

    # Check environment
    for var in REQUIRED_ENV_VARS:
        if not os.environ.get(var):
            print()
            print_skip_message(var)
            sys.exit(0)

    config = check_environment()
    assert config is not None  # Guaranteed by the check above

    run_live_spike(config)


if __name__ == "__main__":
    main()
