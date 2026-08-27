# Live Microsoft Foundry Validation

## Purpose

This bounded validation confirms that a predeployed model returns structured function calls, that
client-observed calls can be normalized without portal-only traces, and that a structured process
evaluation result can be consumed programmatically. It uses synthetic inputs only.

## Validated configuration

| Component | Version or status |
|---|---|
| Foundry project SDK | `azure-ai-projects==2.4.0` |
| Evaluation SDK | `azure-ai-evaluation==1.18.3` |
| Identity SDK | `azure-identity==1.25.3` |
| OpenAI SDK | `openai==3.3.1` |
| Structured-tool deployment | Compatible deployment validated |

The project endpoint has the form
`https://<resource>.services.ai.azure.com/api/projects/<project>`. Authentication uses
`DefaultAzureCredential`; API keys and client secrets are not supported by this workflow.

## Required behavior

Before invoking the experimental process evaluator or replacing recorded evidence, the script
requires both deterministic control paths:

- Passing: `verify_entitlement -> get_claim_summary`.
- Negative control: `get_claim_summary` without prior entitlement.

The script fails closed if either trajectory is missing or ordered incorrectly. A tested non-GPT
deployment returned tool-like text rather than structured calls and was correctly rejected. This is
a deployment compatibility result, not evidence that the authorization control passed.

## Confirmed findings

- Responses returned structured function name, JSON arguments, call ID, final response, and usage.
- Function results were captured client-side when submitted back to the model.
- The configured deployment produced the required passing and negative-control trajectories.
- `ToolCallAccuracyEvaluator` accepted converter-format function calls and returned a serializable
  result with score `5.0` and `passed=true`.
- Sanitized passing and broken recordings replay without Azure access.

## Limitations

- `ToolCallAccuracyEvaluator` is experimental.
- It requires converted calls and flattened function definitions; raw Responses objects are not
  accepted directly.
- Provider trace export remains separate if server-side spans are required.
- The exact minimum OIDC/RBAC assignment remains environment-specific.
- A process-evaluator score never overrides deterministic authorization checks.

## Run

Set `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_DEPLOYMENT_NAME`, authenticate with Microsoft Entra ID, and
run:

```text
python spikes/foundry_process_evaluation/run_spike.py
```

Missing configuration produces an explicit `SKIPPED` result. A successful run writes sanitized
findings and refreshes the recorded bundles; it never silently substitutes fake live results.
