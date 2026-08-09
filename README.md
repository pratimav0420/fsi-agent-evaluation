# FSI Agent Evaluation Starter Kit

## What This Kit Proves

Traditional software testing breaks down when an AI agent can take multiple
valid paths to the same outcome — or confidently take a wrong one. This starter
kit proves that **enterprise agent evaluation** can be:

1. **Traceable** — every evaluation criterion ties back to a documented
   business requirement.
2. **Risk-gated** — release decisions use severity-aware quality bars, not
   subjective review.
3. **Automated** — evaluation pipelines run in CI/CD, not in notebooks after
   the fact.
4. **Progressive** — teams start with deterministic assertions and layer in
   model-based judgment only where objectivity ends.

The reference scenario is a small, intentionally imperfect **Personal Auto
Post-FNOL Claims Servicing Agent** built on Microsoft Foundry. It is a teaching
vehicle, not a production system.

---

## Who This Is For

| Persona | They need to… |
|---------|---------------|
| **CSAs & Architects** | Understand the evaluation pattern and advise customers |
| **AI Developers** | Customize evaluations for their own agents |
| **Platform / Governance Teams** | Operationalize evaluation pipelines and release gates |

---

## What This Is _Not_

- Not a compliance certification tool.
- Not a full-featured claims processing system.
- Not a benchmark of model capabilities.
- Not a replacement for domain-specific risk frameworks.

---

## Repository Structure

```
├── README.md                        ← You are here
├── docs/
│   ├── 01-product-charter.md        ← Scope, users, success criteria
│   └── decisions/
│       └── ADR-001-reference-scenario.md
├── workshop/
│   └── learning-path.md             ← L100 → L200 → L300 progression
├── src/                             ← (Week 2+) Sample agent & evaluators
├── evaluations/                     ← (Week 2+) Test sets & configs
├── .github/workflows/               ← (Week 2+) CI/CD pipelines
└── data/                            ← (Week 2+) Synthetic datasets
    ├── golden/                      ← Hand-authored release-gating cases
    ├── candidates/                  ← Generated cases awaiting approval
    ├── adversarial/                 ← Edge-case and boundary tests
    ├── regression/                  ← Cases from resolved past failures
    └── offline-bundle/              ← Recorded outputs for L100 workshop
```

> Directories marked **(Week 2+)** do not exist yet. They are shown to
> communicate intended structure.

---

## Key Design Principles

1. **Requirement → Evaluation traceability.** Every eval maps to a
   requirement ID.
2. **Deterministic first.** If a behavior can be objectively verified (e.g.,
   "agent must not call the payment tool before verifying entitlement"),
   use assertions — not LLM judges.
3. **Model-based evaluators for semantic judgment only.** Use them where human
   raters would disagree on exact wording but agree on intent.
4. **Evaluation evidence ≠ runtime enforcement.** Eval results inform release
   decisions; they do not act as runtime guardrails.
5. **Synthetic data only.** No real customer data in this repository.

---

## Getting Started

This repository is in **product-definition phase** (Week 1). Start with:

1. [Product Charter](docs/01-product-charter.md) — understand scope and goals.
2. [Learning Path](workshop/learning-path.md) — find your entry point by
   experience level.
3. [ADR-001](docs/decisions/ADR-001-reference-scenario.md) — why personal auto
   claims servicing?

When Week 2 artifacts land, L100 learners will use a **prepared offline
evaluation bundle** — no Azure access required — to run a baseline evaluation,
inspect one agent trace, and explain why a critical control failure blocks
release, all within 20 minutes. An optional live mode reproduces the same
evaluation against a Foundry endpoint.

---

## Contributing

Contribution guidelines will be added when the repository moves to
implementation phase.

---

## License

TBD — intended to be released under MIT.
