# Product Charter — FSI Agent Evaluation Starter Kit

## Problem Statement

Financial services organizations adopting AI agents face a gap between
"the agent works in a demo" and "we can release this with confidence."
Evaluation approaches today tend to be:

- **Too generic** — measure fluency and coherence but not domain-specific
  correctness or safety controls.
- **Too manual** — rely on human review of conversation logs with no
  repeatable automation.
- **Disconnected from requirements** — evaluations exist in notebooks with no
  link to business acceptance criteria or release decisions.

This kit demonstrates how to apply **existing Microsoft Foundry evaluation
capabilities** through FSI-specific requirement traceability, deterministic
controls, process evaluation, severity-aware release gates, evidence retention,
and regression workflows.

---

## Target Users

### 1. CSAs and Solution Architects
- **Need:** A referenceable pattern to advise FSI customers on agent evaluation
  strategy.
- **Success looks like:** Can walk a customer through the evaluation lifecycle
  in < 60 minutes using this kit.

### 2. AI Developers
- **Need:** A working codebase they can fork and adapt for their own agent.
- **Success looks like:** Can replace the sample agent with their own and have
  meaningful evaluations running in CI within a day.

### 3. Platform and Governance Teams
- **Need:** Evidence that evaluation pipelines can enforce quality gates without
  blocking velocity.
- **Success looks like:** Can point to pipeline configuration that demonstrates
  automated release gating with audit-ready evidence.

---

## Differentiation

This kit is not a new evaluation framework. It applies existing Microsoft
Foundry capabilities in an FSI-specific composition:

| Capability applied | What the kit adds |
|---|---|
| Foundry cloud evaluation SDK | FSI requirement-to-evaluation traceability and CI/CD orchestration |
| Built-in quality & safety evaluators | Severity-aware gate configuration with evidence retention |
| Agent process/tool-call evaluators | Domain-specific trajectory assertions for claims servicing workflows |
| Structured evaluation results | Programmatic gate transformation and regression detection |

The differentiation is **the composition and FSI contextualization**, not the
underlying evaluation primitives.

---

## Reference Scenario

**Personal Auto Post-FNOL Claims Servicing Agent**

The agent assists policyholders after a First Notice of Loss has already been
recorded. It operates within a narrow, well-defined decision boundary.

### The agent may:

- Verify claim-level entitlement (is this caller associated with this claim?)
- Retrieve existing claim status
- Retrieve required-document information
- Retrieve applicable policy excerpts
- Explain a determination already recorded by an authorized professional
- Create a human escalation

### The agent may NOT:

- Initiate FNOL
- Determine coverage
- Approve or deny claims
- Modify claim data
- Authorize or estimate payments
- Make fraud determinations
- Provide a binding policy interpretation

---

## Scope

### In Scope

- Reference personal auto post-FNOL claims servicing agent (intentionally minimal).
- Tiered synthetic datasets: golden (hand-authored), candidate (generated,
  human-approved), adversarial, and regression.
- Requirement-to-evaluation traceability matrix.
- Deterministic assertion evaluators for objective behaviors (separated suite).
- Model-based evaluators for semantic quality (separated suite).
- Agent process evaluation (user-defined function tools; custom assertions
  for critical FSI invariants).
- Combined requirement-traceable release report across all evaluation suites.
- Failure analysis patterns (root-cause categorization of eval failures).
- CI/CD pipeline (GitHub Actions with OIDC — runnable; Azure DevOps — documented).
- Severity-aware release gates (Critical / High / Medium / Informational).
- Offline L100 evaluation bundle (no Azure access required).
- Production feedback loop (L300 documented pattern, not deployed).
- Progressive learning content (L100, L200, L300).

### Non-Goals

- Production-ready claims processing system.
- Regulatory compliance certification or attestation.
- Runtime guardrails or enforcement (evaluation only).
- Real customer or policyholder data.
- Performance benchmarking of foundation models.
- Multi-cloud agent platform support (Microsoft Foundry only).
- Custom UI or dashboard (use existing Foundry UX).
- Coverage determination, payment authorization, or fraud detection logic.

---

## Deliverables

| # | Deliverable | L-Level | August Week |
|---|---|---|---|
| D1 | Product charter and ADRs | L100 | 1 |
| D2 | Reference agent (personal auto claims servicing) | L200 | 2 |
| D3 | Golden dataset (20 hand-authored cases) + requirement traceability matrix | L200 | 2 |
| D3a | Offline L100 evaluation bundle (recorded outputs, traces, results, gate decisions) | L100 | 2 |
| D4 | Deterministic evaluator suite | L200 | 3 |
| D5 | Model-based evaluator suite | L200–L300 | 3 |
| D6 | Process evaluator (function-tool assertions + custom FSI invariant checks) | L300 | 3 |
| D7 | GitHub Actions pipeline with OIDC auth and severity-aware release gates | L200 | 4 |
| D8 | Failure analysis tooling | L300 | 4 |
| D9 | Production feedback loop (documented pattern) | L300 | 4 |

---

## Measurable Success Criteria

1. **Traceability coverage:** 100% of evaluation test cases link to a
   documented requirement ID.
2. **Pipeline execution:** GitHub Actions workflow completes eval suite in
   < 10 minutes on synthetic data.
3. **Gate reliability:** A deliberately degraded agent version fails the
   release gate in CI (demonstrated via a "bad build" test case).
4. **Time-to-first-result:** A new user runs the prepared baseline evaluation
   and sees results in under 20 minutes.
5. **Progressive adoption:** A new user can run the offline baseline before
   moving into customization and live operationalization.
6. **Zero real data:** Repository passes automated scan confirming no PII
   or real policy/claim identifiers.

### August Adoption Targets

| Target | Measure |
|---|---|
| 5 CSA users | Unique users who complete L100 run-and-interpret exercise |
| 2 customer application mappings | CSAs who map the pattern to a real customer scenario |
| Foundry engineering feedback captured | At least one feedback loop on SDK capability gaps |
| First baseline result in < 20 minutes | Validated via user testing |

---

## Resolved Architecture Decisions

### 1. Process Evaluation Strategy

- Use **user-defined function tools** for the core agent tool surface so
  Foundry process evaluators can trace them.
- Use **custom deterministic assertions** for critical FSI invariants
  (prohibited actions, tool ordering, boundary violations).
- Execute deterministic and model-based evaluations as **separate suites**.
- Combine results into **one requirement-traceable release report**.
- Week 2 spike validates exact Foundry trace formats and process-evaluator
  compatibility (see validation backlog).

**Known limitation:** Foundry process evaluators have limited support for some
tool types, including Azure AI Search. The agent will use user-defined function
tools for retrieval. Custom assertions cover invariants that built-in process
evaluators cannot reach.

### 2. Synthetic Data Strategy

| Tier | Source | Governance |
|---|---|---|
| **Golden** | Hand-authored (initial 20 cases) | Requirement-linked; human-reviewed; release-gating |
| **Candidate** | LLM-generated or template-expanded | Human approval required before promotion |
| **Adversarial** | Hand-authored or promoted from candidate | Targets known edge cases and boundary violations |
| **Regression** | Captured from past failures | Added when a fix resolves a previously failing case |

- Templates produce deterministic expansions (e.g., vary claim types, dates).
- LLM generation is permitted only for candidate cases; never directly
  into golden, adversarial, or release-gating tiers.
- All tiers link back to requirement IDs in the traceability matrix.

### 3. Severity Tiers and Gate Logic

| Severity | Gate behavior |
|---|---|
| **Critical** | Any single failure blocks release. No aggregate score can override. |
| **High** | Designated must-pass cases block individually. Aggregate target: 90% initially. |
| **Medium** | Warning when below 85% or on meaningful regression from baseline. |
| **Informational** | Report only; no gate effect. |

- With small datasets, use explicit **must-pass cases** and **absolute failure
  budgets** (e.g., "≤ 1 High failure allowed") instead of percentages.
- No blended agent score is calculated. Gate decisions use severity precedence
  (see Evaluator Composition below).

### 4. CI Identity and Authentication

- GitHub Actions: **OIDC with federated identity credential** on a Microsoft
  Entra application/service principal.
- Least-privilege Foundry RBAC — exact roles to be confirmed in Week 2.
- **No client secrets or API keys** stored in repository or CI variables.
- Document a **user-assigned managed identity** option for self-hosted Azure
  runner scenarios.

### 5. Evidence Retention

Each evaluation run retains:
- Machine-readable results (JSON).
- Human-readable summary.
- Agent version identifier and commit SHA.
- Requirement ID ↔ test case ID mapping.
- Failed traces (full conversation + tool calls).
- Pipeline metadata (run ID, trigger, duration).

**CI artifact retention defaults:**

| Run type | Retention |
|---|---|
| PR runs | 30 days |
| main / release runs | 90 days |

- Approved release evidence should be exported to **customer-controlled
  durable storage** (organizational policy decision; not enforced by the kit).
- Foundry and Application Insights retention are governed by those services'
  own policies and documented separately.

### 6. Evaluator Composition and Precedence

No single blended agent score. Gate decisions follow strict precedence:

1. **Critical deterministic failure** → block.
2. **Required evaluator error** (evaluator itself fails) → inconclusive → block.
3. **High-risk must-pass failure** → block.
4. **High-risk aggregate threshold breach** → block.
5. **Medium-risk degradation** → warn.
6. **Informational metric** → report only.

Dimension-level scores and individual failure reasons are preserved in the
release report. The report never collapses dimensions into a single number.

### 7. L100 Offline Bundle

The mandatory L100 path (< 20 minutes) uses a **prepared offline evaluation
bundle** shipped in the repository:

- Synthetic inputs (subset of golden dataset).
- Recorded agent outputs.
- Tool-call traces.
- Evaluator results (deterministic + model-based).
- Gate decisions (including one Critical failure for the "explain why it
  blocks" exercise).

An **optional live mode** reproduces the same evaluation against a Foundry
endpoint. Azure access is required only for live mode, not for the prepared
offline baseline.

---

## Assumptions Status

| # | Assumption | Status |
|---|---|---|
| A1 | Foundry cloud evaluation and SDK support CI/CD submission patterns | Confirmed; implementation to validate |
| A2 | Foundry evaluation results are structured (JSON) for programmatic gate logic | Confirmed; gate transformation to validate |
| A3 | Foundry agent process evaluators work with user-defined function tools | Confirmed; tool-type limitations mitigated by design |
| A4 | GitHub Actions OIDC + federated credential + Foundry RBAC | Decided; exact least-privilege roles to validate |
| A5 | Hand-authored + template-expanded synthetic data is realistic for post-FNOL | Requires domain review of initial 20 golden cases |
| A6 | Foundry process evaluators have limited support for some tool types (incl. Azure AI Search) | Known; mitigated by user-defined function tools + custom assertions |

---

## Week 2 Validation Backlog

| # | Validation item | Depends on |
|---|---|---|
| V1 | Confirm function-tool trace serialization format in Foundry | D2 (agent implementation) |
| V2 | Confirm supported Foundry process evaluators against the sample agent's tools | D2, V1 |
| V3 | Confirm structured result retrieval and normalization for gate logic | D4/D5 (evaluator implementation) |
| V4 | Confirm exact least-privilege Foundry RBAC roles for CI service principal | D7 (pipeline implementation) |
| V5 | Validate the offline bundle by recording a real live evaluation run | D3a (offline bundle) |

All items are implementation-phase validations. No architectural decisions
are blocked; the design accommodates fallback paths if validation surfaces
surprises.

---

## Risks

| Risk | Mitigation |
|---|---|
| Foundry eval SDK changes during development | Pin SDK version; abstract evaluation calls behind interface |
| Kit perceived as compliance tool | Explicit disclaimers in README, charter, and release evidence |
| Scope creep beyond post-FNOL servicing boundary | Agent capability boundary documented; PRs adding decision logic rejected |
| Evaluation results misinterpreted as model benchmarks | Documentation clarifies eval measures agent behavior, not model capability |
| Process evaluator tool-type limitations | User-defined function tools + custom assertions; validated in Week 2 spike |
| Percentage-based gates unreliable on small datasets | Must-pass cases and absolute failure budgets used alongside percentages |
| Offline bundle drifts from live behavior | V5 validation re-records bundle from live run; version-stamped |

---

## Stakeholders

- **Owner:** (TBD — assign during kickoff)
- **Reviewers:** FSI domain architects, Foundry product team (for capability validation)
- **Contributors:** CSA community, AI platform engineering

---

## Timeline

| August Week | Focus |
|---|---|
| 1 | Product definition (this document) and ADRs |
| 2 | Reference agent, golden dataset, traceability matrix, offline bundle, validation spike |
| 3 | Evaluator suites (deterministic + model-based + process), combined release report |
| 4 | CI/CD pipeline (OIDC), severity-aware gates, failure analysis, and adoption feedback |
