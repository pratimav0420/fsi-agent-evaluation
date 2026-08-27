# FSI Agent Evaluation Starter Kit

An executable reference for moving an enterprise agent from a convincing demo to requirement-traceable release evidence. The sample is a small Personal Auto Post-FNOL Claims Servicing Agent using synthetic data only.

The kit demonstrates deterministic control assertions, semantic-evaluator extension points, normalized trajectory evidence, severity-aware gates, baseline comparison, failure analysis, and CI/CD integration. It is not a compliance certification tool or a production claims system.

## Quick start

Use Python 3.11 or newer.

```text
python -m pip install -e ".[dev]"
fsi-agent-eval validate
fsi-agent-eval baseline --output artifacts/baseline
fsi-agent-eval broken --output artifacts/broken
fsi-agent-eval compare
fsi-agent-eval replay --bundle data/offline-bundle/live-pass.json
```

The baseline runs five representative synthetic cases. The broken profile intentionally retrieves protected claim data before entitlement verification and must be blocked. To run all 20 curated cases:

```text
fsi-agent-eval baseline --cases evaluations/datasets/seed-cases.yaml --output artifacts/pull-request
```

Each run writes JSON, Markdown, and JUnit-compatible evidence. Azure is not required for offline evaluation.

The recorded live bundle was produced from a sanitized Foundry v1 run. Replaying
`live-broken-order.json` must block on entitlement-before-retrieval.

## Repository map

- `docs/`: product charter, behavioral boundaries, taxonomy, architecture, gate policy, and decisions.
- `evaluations/`: ten requirements, 20 curated cases, and execution profiles.
- `src/fsi_agent_eval/`: provider-neutral contracts, local/fake adapters, tools, evaluators, gates, reporting, and CLI.
- `spikes/`: isolated live Microsoft Foundry validation.
- `failure-lab/`: intentional failures, diagnoses, remediation, and regression links.
- `.github/workflows/`: runnable offline PR gate and approved OIDC-based live validation.

## Design principles

1. Every case and result links to a stable business requirement.
2. Objective behavior uses deterministic assertions; model-based judges are limited to semantic quality.
3. Critical failures and required evaluator errors cannot be averaged away.
4. Gate logic consumes normalized contracts, never raw provider objects.
5. Evaluation evidence informs release decisions but is not a runtime guardrail.
6. No real customer, claim, policy, identity, or Azure configuration belongs in the repository.

Start with the [product charter](docs/01-product-charter.md), [scenario boundaries](docs/02-scenario-and-agent-boundaries.md), and [release gates](docs/06-release-gates.md).

## Live Foundry validation

The optional spike uses `DefaultAzureCredential` and two runtime settings documented in `.env.example`. It captures only sanitized trace-shape and SDK findings. The live path must never silently fall back to fake results.

## License

MIT.
