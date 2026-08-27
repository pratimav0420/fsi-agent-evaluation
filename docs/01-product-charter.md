# Product Charter

## Purpose

The FSI Agent Evaluation Starter Kit demonstrates how to move from an agent demo to
requirement-traceable release evidence. It applies Microsoft Foundry capabilities through
domain-specific requirements, deterministic controls, normalized process evidence, severity-aware
gates, and regression workflows.

This is an implementation reference, not a new evaluation framework, regulatory interpretation,
compliance certification, or production claims system.

## Who this is for

- **Solution architects:** evaluate and explain a practical agent release-assurance pattern.
- **AI developers:** replace the sample adapter and reuse the evaluation contracts and gates.
- **Platform teams:** integrate repeatable checks and retained evidence into delivery pipelines.
- **Risk and governance reviewers:** trace release decisions to explicit requirements and cases.

## Reference scenario

The sample is a synthetic Personal Auto Claims Servicing Agent operating after First Notice of Loss
(FNOL). It may verify claim-level entitlement, retrieve existing status or required-document
information, explain recorded information, and create a human escalation.

It may not initiate a claim, determine coverage, approve or deny a claim, modify claim data,
authorize or estimate payments, determine fraud, or provide binding policy interpretations.

## What the repository implements

- Ten stable `FSI-*` requirements and 20 curated synthetic cases.
- A provider-neutral `AgentAdapter` and normalized run, trace, and evaluation contracts.
- A deterministic local agent and an intentional authorization-ordering failure.
- Deterministic trajectory, authorization, privacy, action-boundary, reliability, and trace checks.
- Severity precedence in which critical failures and required evaluator errors block promotion.
- JSON, Markdown, and JUnit-compatible evidence plus baseline comparison.
- Sanitized live Foundry recordings and credential-free replay.
- GitHub Actions for offline evaluation and an approved OIDC-based live validation path.
- Azure DevOps and production-feedback adoption patterns.

## Design principles

1. Requirements, cases, evaluator results, and evidence use stable identifiers.
2. Objective behavior uses deterministic checks; semantic judgment uses a separate extension point.
3. Critical failures cannot be averaged away.
4. Evaluator errors are inconclusive and block when the evaluator is required.
5. Provider objects remain behind the adapter boundary.
6. Evaluation evidence informs release decisions but is not runtime enforcement.
7. Only synthetic data and sanitized provider evidence belong in the repository.

## Evidence and release decisions

Each run retains versions, case and requirement identifiers, normalized tool calls, evaluator results,
gate reasons, and report artifacts. Default CI retention is 30 days for pull-request evidence and
90 days for `main` or approved live evidence. Organizations remain responsible for their own durable
storage, review, exception, and retention policies.

## Scope boundaries

The repository does not provide:

- Production identity enforcement, monitoring, or gateway controls.
- A user interface or deployable claims application.
- Real policies, claims, identities, endpoints, tenants, or subscriptions.
- Foundation-model benchmarking.
- Automated organizational exception authority.
- A claim of regulatory compliance, certification, or fitness for a particular production use.

## Current validation status

- The 20-case deterministic baseline passes 150 of 150 checks.
- The intentional authorization-ordering build is blocked with 12 findings.
- A sanitized live run produced the required structured tool trajectory.
- The recorded passing bundle replays successfully; the negative control is blocked.
- Unit tests, Ruff, strict mypy, schema validation, and traceability validation pass.

The remaining environment-specific task is confirming the minimum OIDC/RBAC assignment for an
approved GitHub Actions identity.
