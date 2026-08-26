# Foundry v1 Process Evaluation Spike

## Status

Executed successfully on August 9, 2026 using synthetic inputs and Microsoft Entra authentication. Committed findings contain no resource, project, tenant, subscription, response, or tool-call identifiers.

## Validated stack

| Package | Version |
|---|---|
| azure-ai-projects | 2.4.0 |
| azure-ai-evaluation | 1.18.3 |
| azure-identity | 1.25.3 |
| openai | 2.53.0 |

The spike uses a Foundry v1 project endpoint (`.../api/projects/<project>`) and `DefaultAzureCredential`. The earlier connection-string and Threads/RunSteps design was obsolete for the validated service surface.

## Confirmed behavior

- The project client enumerates deployments and returns an authenticated OpenAI client.
- Responses returns a structured function call with name, JSON arguments, and a call ID.
- Tool outputs are supplied by the client using `function_call_output` and captured client-side.
- A passing live run produced `verify_entitlement -> get_claim_summary`.
- An intentional live failure produced `get_claim_summary` without entitlement.
- Response usage metadata was available.
- `ToolCallAccuracyEvaluator` accepted converter-format calls and returned a serializable dictionary with score 5.0 and `passed=true`.

## Limitations

- `ToolCallAccuracyEvaluator` is explicitly experimental in azure-ai-evaluation 1.18.3.
- It requires `{type, name, arguments, tool_call_id}` calls and flattened function definitions; raw Responses objects are not accepted directly.
- Responses provides client-observed trajectory evidence. Provider trace export remains a separate validation if server-side spans are required.
- Exact least-privilege RBAC roles were not reduced empirically; the authenticated identity had sufficient existing access.

## Fail-closed trajectory validation

The spike deterministically validates both live control paths before invoking the model-based
evaluator or replacing recorded evidence:

- The passing run must produce exactly `verify_entitlement -> get_claim_summary`.
- The negative control must retrieve a claim summary without prior entitlement verification.

An August 25, 2026 rerun against a configured non-GPT deployment returned tool-like text instead
of structured function calls. The experimental evaluator had previously scored the empty call list
as passing, so the spike now rejects that result and preserves the last known-good sanitized
recordings. This is a deployment/tool-compatibility finding, not evidence that the required control
passed.

An August 26, 2026 rerun against GPT-4.1 produced structured calls for both control paths. The
passing path emitted `verify_entitlement -> get_claim_summary`; the negative control emitted
`get_claim_summary` without prior entitlement. Both deterministic validation and the structured
Tool Call Accuracy result completed successfully, and the sanitized recordings were refreshed.

## Run

Set `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_MODEL_NAME`, authenticate with Entra ID, then run `python spikes/foundry_process_evaluation/run_spike.py`.

With missing configuration, the script prints `SKIPPED` and never creates fake findings. Successful execution writes sanitized findings and replaces the L100 recorded bundles.
