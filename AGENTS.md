# Repository Guidance

This repository demonstrates requirement-traceable evaluation for a synthetic Personal Auto Post-FNOL Claims Servicing Agent.

- Treat `evaluations/specifications/requirements.yaml` and `evaluations/datasets/seed-cases.yaml` as authoritative evaluation contracts.
- Use synthetic data only. Never add real customer, policy, claim, identity, endpoint, tenant, or subscription data.
- Do not claim regulatory compliance or certification.
- Keep Foundry SDK objects behind `AgentAdapter`; gates consume normalized contracts only.
- Link every case and evaluator result to stable `FSI-*` requirement IDs.
- Prefer deterministic assertions for objective behavior and model-based judgment only for semantics.
- Critical failures cannot be averaged away. Evaluator errors are Inconclusive and block promotion.
- Validate with `python -m fsi_agent_eval.cli validate`, run offline profiles with `baseline` and `broken`, then run tests, Ruff, and mypy.
