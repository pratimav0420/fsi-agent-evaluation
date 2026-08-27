# Contributing

Contributions should preserve the repository's requirement traceability, synthetic-data boundary,
and provider-neutral gate contracts.

## Setup

Use Python 3.11 or newer in a virtual environment:

```text
python -m pip install -e ".[dev]"
```

Install `.[azure,dev]` only when reproducing the optional live Foundry validation.

## Change expectations

- Link every new case and evaluator result to a stable `FSI-*` requirement.
- Use deterministic assertions for objective behavior.
- Keep provider SDK objects behind `AgentAdapter`.
- Use synthetic data only.
- Do not commit endpoints, tenant or subscription identifiers, credentials, or customer data.
- Do not claim regulatory compliance or certification.
- Preserve fail-closed behavior for critical controls and evaluator errors.

## Validation

Run before opening a pull request:

```text
python -m fsi_agent_eval.cli validate
python -m fsi_agent_eval.cli baseline --cases evaluations/datasets/seed-cases.yaml --output artifacts/baseline
python -m fsi_agent_eval.cli broken --cases evaluations/datasets/seed-cases.yaml --output artifacts/broken
python -m pytest --cov=fsi_agent_eval --cov-fail-under=70
python -m ruff check .
python -m mypy src tests
```

The broken profile is expected to exit nonzero and report a blocked gate.

## Pull requests

Describe the requirement IDs affected, why the behavior changed, the evidence produced, and the
commands used to validate it. Keep unrelated changes separate.
