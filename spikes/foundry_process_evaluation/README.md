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

## Run

Set `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_MODEL_NAME`, authenticate with Entra ID, then run `python spikes/foundry_process_evaluation/run_spike.py`.

With missing configuration, the script prints `SKIPPED` and never creates fake findings. Successful execution writes sanitized findings and replaces the L100 recorded bundles.
