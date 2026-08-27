# Documentation Guide

Use this guide to move from orientation to implementation.

## Start here

1. [Product charter](01-product-charter.md) - purpose, audience, scope, and validation status.
2. [Scenario boundaries](02-scenario-and-agent-boundaries.md) - what the sample agent may and may not do.
3. [Requirements catalog](03-requirements-catalog.md) - the ten release requirements.
4. [Evaluation taxonomy](04-evaluation-taxonomy.md) - how checks are organized.
5. [Reference architecture](05-reference-architecture.md) - components and evidence flow.
6. [Release gates](06-release-gates.md) - pass, warn, block, and inconclusive behavior.

## Operational patterns

- [Azure DevOps pattern](07-azure-devops-pattern.md)
- [Production feedback loop](08-production-feedback-loop.md)
- [Live Foundry validation](../spikes/foundry_process_evaluation/README.md)
- [Failure analysis](../failure-lab/README.md)

## Decisions

- [ADR-001: Reference scenario](decisions/ADR-001-reference-scenario.md)
- [ADR-002: Evaluation strategy](decisions/ADR-002-evaluation-strategy.md)
- [ADR-003: Requirement and case schemas](decisions/ADR-003-requirement-schema.md)

## Glossary

- **FSI:** Financial services industry.
- **FNOL:** First Notice of Loss, the initial report that creates an insurance claim.
- **Entitlement:** Claim-specific confirmation that the caller may access protected information.
- **Trajectory:** The ordered tool calls, arguments, results, authorization state, and errors in a run.
- **Deterministic evaluator:** A code-based check with an objective expected result.
- **Semantic evaluator:** A rubric-based judge for meaning or response quality.
- **Must-pass:** A case whose failure blocks release regardless of aggregate performance.
