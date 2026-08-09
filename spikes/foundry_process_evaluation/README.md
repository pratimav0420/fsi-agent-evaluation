# Foundry Process Evaluation Spike

## Purpose

Validate the Week 2 backlog items against a real Microsoft Foundry endpoint:

1. What tool-call information is returned for a user-defined function tool?
2. Can that information be normalized without depending on a portal-only trace?
3. Which current Foundry agent/process evaluators accept the captured format?
4. Can structured evaluation results be retrieved programmatically?
5. Which exact SDK versions and APIs were validated?

## Status

**Not yet executed** — awaiting Foundry endpoint configuration.

---

## Prerequisites

```bash
# Required environment variables (see ../../.env.example)
export AZURE_AI_PROJECT_CONNECTION_STRING="<your-foundry-project-connection-string>"
export AZURE_AI_AGENT_MODEL_DEPLOYMENT="<your-model-deployment-name>"
```

Authentication uses `DefaultAzureCredential` (Azure CLI login, managed identity,
or VS Code credential). No API keys or client secrets.

## Running the Spike

```bash
cd spikes/foundry_process_evaluation
python run_spike.py
```

If required environment variables are absent, the spike exits with:
```
SKIPPED: Missing required environment variable: AZURE_AI_PROJECT_CONNECTION_STRING
Set up instructions: see ../../.env.example
```

## SDK Versions Under Test

| Package | Version | Status |
|---|---|---|
| azure-ai-agents | 1.2.0b5 | Installed |
| azure-ai-projects | 2.0.0b1 | Installed |
| azure-ai-evaluation | 1.18.3 | To install for live spike |
| azure-identity | 1.19.0 | Installed |

---

## Findings

### Confirmed Behavior

*(To be filled after spike execution)*

### Observed Limitations

**From SDK inspection (pre-execution):**

- `RunStepFunctionToolCallDetails` contains only `name` and `arguments` —
  **no `output` field**. Tool outputs submitted via `submit_tool_outputs`
  are not reflected back in the RunStep's tool_calls list.
- This means tool output must be captured **client-side** at the time of
  submission, or retrieved via a separate mechanism.
- `RunStep` provides timing (`created_at`, `completed_at`) and token `usage`.
- `ThreadRun` provides `model` identifier and aggregate usage.
- `RunStepToolCall` has only `id` and `type` at the base level.

**Implication for normalization:**
The adapter must record tool outputs at submission time and merge them with
RunStep data to produce a complete `ToolCallRecord`. Relying solely on
RunStep retrieval will yield arguments but NOT results.

### Untested Assumptions

1. Whether `azure-ai-evaluation` process evaluators accept the trace format
   produced by `azure-ai-agents` RunStep data.
2. Whether evaluation results from `azure-ai-evaluation` are structured JSON
   retrievable programmatically (not just portal display).
3. Exact RBAC roles required for a service principal to submit evaluation runs.
4. Whether RunStep `usage` is populated for function-tool steps (vs. only
   message-creation steps).

### Recommended Week 2 Implementation Choice

Based on SDK inspection:

1. **Capture tool outputs at submission time.** The adapter must intercept or
   record the output string passed to `submit_tool_outputs` and associate it
   with the corresponding `tool_call_id`.
2. **Merge RunStep metadata with captured outputs.** Build the normalized
   `ToolCallRecord` from: RunStep (timing, call ID, function name, arguments)
   + client-captured output (result string).
3. **Do not depend on a single API call for complete traces.** The full
   picture requires: ThreadRun (model, aggregate usage) + RunSteps (per-step
   details) + client-captured outputs.
4. **Validate process evaluator input format** in the live spike before
   committing to a specific evaluator integration pattern.

---

## Output

Sanitized example outputs are saved to `expected_outputs/` after successful
live execution. No tokens, subscription IDs, endpoints, tenant IDs, or other
secrets are included in committed output.
