# ADR-001: Reference Scenario Selection

## Status

Accepted (revised 2026-08-07)

## Date

2026-08-07

## Context

The starter kit needs a reference scenario to ground all evaluation examples.
The scenario must be:

1. **Familiar to FSI audiences** — immediately recognizable without domain
   training.
2. **Rich enough for multi-step agent behavior** — requires tool calls,
   conditional logic, and varied conversation paths.
3. **Small enough to be a teaching vehicle** — must not become a production
   system.
4. **Safe to synthesize** — realistic synthetic data must be achievable without
   access to real policies or claims.
5. **Demonstrative of evaluation challenges** — should naturally produce
   scenarios where deterministic and model-based evaluators are both needed.
6. **Narrowly bounded** — the agent's decision authority must be unambiguous
   so evaluation criteria are testable.

## Decision

We will use **Personal Auto Post-FNOL Claims Servicing** as the reference
scenario. The agent assists policyholders after a First Notice of Loss has
already been recorded.

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

This boundary ensures the agent never makes consequential decisions — it only
retrieves, explains, and escalates.

## Alternatives Considered

| Alternative | Why rejected |
|---|---|
| **Broad claims servicing (multi-line)** | Decision boundary too ambiguous across P&C, Life, Health; hard to define universal eval criteria |
| **Loan origination** | Too complex for a starter kit; requires deep product knowledge to synthesize realistic data |
| **Account balance / transaction inquiry** | Too simple; mostly retrieval with few multi-step evaluation challenges |
| **Investment advisory** | Regulatory sensitivity too high; even synthetic examples could be misinterpreted as advice |
| **KYC / onboarding** | Heavy on document processing; shifts focus from agent evaluation to OCR/extraction quality |
| **Insurance underwriting** | Decision complexity too high for a reference; risk of scope creep into actuarial logic |
| **Full FNOL intake** | Includes data creation (new claim); blurs the "retrieve/explain only" boundary |

## Consequences

### Positive

- Personal auto is a broadly recognizable insurance scenario with clear
  servicing boundaries.
- Post-FNOL servicing has a clear decision boundary: the agent retrieves and
  explains but never decides.
- Multi-turn conversations with branching paths (status check → document
  request → escalation) naturally exercise process evaluation.
- Determination explanations require empathy and completeness — good fit for
  model-based evaluators.
- Entitlement verification and prohibited-action boundaries are good fits for
  deterministic assertions.
- Synthetic post-FNOL data is straightforward to generate without actuarial
  expertise.

### Negative

- Non-insurance FSI audiences (banking, capital markets) may not immediately
  see themselves in the scenario. Mitigation: documentation explicitly states
  the evaluation pattern is transferable to any agent with similar tool-call
  and boundary characteristics.
- Personal auto is US-centric terminology. Mitigation: include a minimal
  glossary; note that "motor claims" is the equivalent term in other markets.
- Narrowing to post-FNOL excludes intake scenarios. Mitigation: treat FNOL
  intake as a separate extension with its own authority boundaries.

### Architectural Consideration

Foundry process evaluators have limited support for some tool types, including
Azure AI Search. The resolved approach for this kit:

1. **User-defined function tools** for the core agent tool surface, ensuring
   Foundry process evaluators can trace them.
2. **Custom deterministic assertions** for critical FSI invariants
   (prohibited actions, tool ordering, boundary violations) that built-in
   process evaluators cannot reach.
3. **Separated evaluation suites** (deterministic and model-based) combined
   into one requirement-traceable release report.

Live validation confirmed structured function-call capture with a compatible deployment. The
spike fails closed when a deployment returns tool-like text instead of
structured calls.

## References

- Product Charter: `docs/01-product-charter.md`
