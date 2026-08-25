# Release Gates

## Profiles

- `local-smoke`: five representative offline cases for fast development feedback.
- `pull-request`: deterministic controls and schema/traceability validation.
- `pre-release`: all 20 cases plus approved model-based and live Foundry suites.
- `continuous`: sampled, sanitized production-derived candidates; report-first until promoted.

## Precedence

1. A Critical deterministic failure blocks.
2. A required evaluator error yields Inconclusive and blocks promotion.
3. A High must-pass failure blocks.
4. More than one non-must-pass High failure breaches the initial absolute budget and blocks.
5. A Medium failure warns.
6. Informational findings report only.

No aggregate score can override an individual control. With only 20 cases, explicit must-pass flags and absolute budgets take precedence over percentages.

## Baselines and exceptions

A baseline comparison reports newly blocking findings and gate regression. Baseline improvement cannot hide a Critical failure. Exceptions require a named owner, rationale, expiration, affected requirement/cases, compensating review, and retained approval; this kit documents but does not automate organizational exception authority.

## Evidence retention

Retain JSON results, Markdown summary, JUnit output, versions, requirement/test mapping, failed traces, and pipeline metadata. Default retention is 30 days for PR runs and 90 days for main/release runs. Long-term retention is an organizational policy.
