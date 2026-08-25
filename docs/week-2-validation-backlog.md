# Week 2 Validation Backlog

Items requiring empirical validation against a live Microsoft Foundry endpoint.
These validate architecture decisions made in Week 1; no architectural changes
are blocked, but implementation choices may need adjustment.

## V1: Function-Tool Trace Serialization

**Question:** What exact data is available in RunStep for user-defined function tools?

**Pre-spike finding (from SDK inspection):**
- `RunStepFunctionToolCallDetails` has only `name` and `arguments`.
- No `output` field — tool results must be captured client-side at submission.
- `RunStep` provides `id`, `created_at`, `completed_at`, `usage`.

**Validation needed:**
- Confirm RunStep serialization matches SDK inspection in live environment.
- Confirm timing fields are populated for function-tool steps.
- Confirm `usage` is populated (or determine if it's only on message steps).
- Document the exact JSON shape for normalization code.

**Status:** Complete for the Foundry v1 Responses surface. Structured function name, JSON
arguments, call ID, final response, and usage were observed. Tool results remain client-captured.

---

## V2: Supported Process Evaluators

**Question:** Which Foundry agent/process evaluators accept traces from
user-defined function tools?

**Validation needed:**
- Install `azure-ai-evaluation` and enumerate available process evaluators.
- Determine input format requirements for each evaluator.
- Test whether RunStep data (without output) is sufficient, or whether
  client-captured outputs must be included.
- Document any evaluators that explicitly do NOT support function tools.

**Status:** Partially complete. `ToolCallAccuracyEvaluator` accepted converter-format function
calls and returned a structured result. It is experimental; broader evaluator coverage is optional.

---

## V3: Structured Result Retrieval

**Question:** Can evaluation results be retrieved as structured JSON for
programmatic gate logic?

**Validation needed:**
- Run an evaluation using `azure-ai-evaluation` SDK.
- Confirm results are returned as typed objects or dicts (not just displayed).
- Document the result schema (fields, nesting, score formats).
- Confirm results can be serialized to JSON for CI artifact retention.

**Status:** Complete. The evaluator returned a serializable dictionary containing status, score,
threshold, reason, and pass fields.

---

## V4: Least-Privilege RBAC Roles

**Question:** What are the exact minimum RBAC roles for a CI service principal
to submit agent runs and evaluation runs?

**Validation needed:**
- Identify required roles for: agent creation, thread/run management,
  evaluation submission, result retrieval.
- Test with a service principal that has ONLY the identified roles.
- Document the role assignment commands.
- Confirm OIDC federated credential works with these roles.

**Status:** Open. Authentication and project/deployment access succeeded, but least-privilege role
reduction was not tested against a dedicated identity.

---

## V5: Offline Bundle Generation

**Question:** Can a live evaluation run be captured and replayed as an offline
bundle for the L100 workshop?

**Validation needed:**
- Run the full evaluation cycle (agent run → evaluation → gate decision).
- Capture all artifacts: inputs, outputs, traces, evaluator results, gate.
- Strip secrets/identifiers and save as the offline bundle.
- Verify the offline bundle can be consumed without Azure access.
- Confirm the bundle is version-stamped to detect drift.

**Status:** Complete. Sanitized passing and authorization-order failure recordings are stored in
`data/offline-bundle` and replay without Azure access.

---

## Completion Criteria

All items complete when:
- [ ] V1: Trace format documented with example JSON (sanitized).
- [ ] V2: Evaluator compatibility matrix documented.
- [ ] V3: Result retrieval confirmed with example (sanitized).
- [ ] V4: RBAC roles documented with CLI commands.
- [ ] V5: Offline bundle generated and verified.
