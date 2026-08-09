# Learning Path — FSI Agent Evaluation Starter Kit

This document maps a progressive learning journey across three levels:

- **L100** — Run and interpret.
- **L200** — Customize and diagnose.
- **L300** — Operationalize and govern.

Each level is **self-contained** — an L100 learner achieves meaningful outcomes
without needing L200 or L300 material.

---

## L100 — Run and Interpret

**Audience:** CSAs, architects, technical decision-makers, anyone new to agent
evaluation.

**Prerequisite knowledge:** Familiarity with AI agents (what they do, not how
to build one). Ability to run a CLI command and read JSON output.

**Azure access required?** No. The mandatory path uses a prepared **offline
evaluation bundle** containing recorded agent outputs, tool-call traces,
evaluator results, and gate decisions. An optional live mode reproduces the
same evaluation against a Foundry endpoint (requires Azure).

### Outcomes

After completing L100, the learner can:

1. **Run** the prepared baseline evaluation using the offline bundle against
   the sample Personal Auto Post-FNOL Claims Servicing Agent.
2. **Inspect** one agent trace and identify which tools were called, in what
   order, and what the agent returned.
3. **Explain** why a Critical control failure (e.g., agent called a prohibited
   tool) blocks release — connecting it to the requirement traceability
   matrix and the severity precedence rules.
4. Articulate the difference between deterministic assertions and model-based
   evaluators, and when to use each.
5. Identify the four evaluation dimensions used in this kit:
   - **Correctness** — Did the agent produce the right answer?
   - **Safety** — Did the agent avoid prohibited behaviors?
   - **Process** — Did the agent take a valid tool-call path?
   - **Quality** — Was the interaction empathetic, complete, and professional?
6. Describe what a severity-aware release gate is (Critical / High / Medium /
   Informational) and how it differs from a simple pass/fail.

### Content Map

| Asset | Format | Duration |
|---|---|---|
| README.md | Read | 5 min |
| Product Charter | Read | 10 min |
| Run baseline evaluation (offline bundle) | CLI exercise | 10 min |
| Inspect trace + explain gate failure | Guided exercise | 15 min |
| Evaluation dimensions explainer | One-pager | 5 min |

**Total L100 time: ~45 minutes (< 20 minutes for the run-and-interpret core)**

---

## L200 — Customize and Diagnose

**Audience:** AI developers building or adapting agents on Microsoft Foundry.

**Prerequisite knowledge:** L100 outcomes achieved. Python proficiency.
Familiarity with CI/CD concepts. Access to an Azure subscription with Foundry.

### Outcomes

After completing L200, the learner can:

1. Add a new deterministic evaluator for a custom requirement.
2. Add a new model-based evaluator with a custom rubric.
3. Author a new golden case and expand it with templates.
4. Promote a candidate case to the golden or adversarial tier after review.
5. Map a new business requirement to an evaluation test case
   (extend the traceability matrix).
6. Run the GitHub Actions pipeline on a fork and observe release gate
   behavior.
7. Intentionally degrade the agent and confirm the pipeline catches the
   regression.
8. Diagnose a failing evaluation — determine whether the root cause is
   agent logic, retrieval, prompt, or data.

### Content Map

| Asset | Format | Duration |
|---|---|---|
| Local setup guide | Markdown + script | 20 min |
| "Your First Evaluator" tutorial | Step-by-step markdown | 30 min |
| Traceability matrix walkthrough | Markdown | 15 min |
| Synthetic data extension guide | Markdown | 20 min |
| CI/CD pipeline fork-and-run guide | Markdown | 20 min |
| "Break the Agent" exercise | Guided exercise | 20 min |
| Failure diagnosis walkthrough | Markdown + exercise | 20 min |

### Hands-On Exercises

| # | Exercise | Skill Practiced |
|---|---|---|
| E1 | Add a requirement: "Agent must verify entitlement before retrieving claim details" | Traceability |
| E2 | Write a deterministic evaluator asserting entitlement check precedes status retrieval | Assertion design |
| E3 | Write a model-based evaluator scoring empathy in determination explanations | Rubric design |
| E4 | Author 3 new golden cases for document-request scenarios; template-expand to 10 | Data authoring + tier governance |
| E5 | Push a commit that fails the release gate | CI/CD comprehension |
| E6 | Diagnose why an evaluator fails: is it the agent, the data, or the evaluator? | Root-cause analysis |

---

## L300 — Operationalize and Govern

**Audience:** Platform engineers, MLOps teams, governance/risk teams
operationalizing evaluation at scale.

**Prerequisite knowledge:** L200 outcomes achieved. Experience with CI/CD
pipeline design, infrastructure-as-code, and organizational release processes.

### Outcomes

After completing L300, the learner can:

1. Design a process evaluator that scores multi-step agent tool-call
   sequences against expected patterns using function-tool traces.
2. Implement failure analysis workflows that categorize evaluation failures
   by root cause (agent logic, retrieval, model, data).
3. Configure severity-tiered release gates using the kit’s precedence model
   (Critical = block; High = must-pass + threshold; Medium = warn;
   Informational = report).
4. Integrate evaluation evidence into existing audit/compliance reporting
   workflows (without claiming compliance).
5. Design a production feedback loop pattern: collect real interaction signals
   → identify coverage gaps → generate new eval cases → promote through
   candidate → golden tier.
6. Adapt the pipeline for Azure DevOps (documented pattern).
7. Address Foundry process evaluator tool-type limitations using custom
   assertions or separated evaluation suites.

### Content Map

| Asset | Format | Duration |
|---|---|---|
| Process evaluation deep-dive | Markdown + code | 45 min |
| Failure analysis patterns guide | Markdown + notebook | 30 min |
| Release gate configuration reference | YAML + markdown | 20 min |
| Production feedback loop pattern | Diagram + markdown | 30 min |
| Azure DevOps adaptation guide | Markdown | 20 min |
| Tool-type limitation workarounds | Markdown + code | 30 min |

### Hands-On Exercises

| # | Exercise | Skill Practiced |
|---|---|---|
| E7 | Define expected tool-call sequences for 3 post-FNOL scenarios | Process specification |
| E8 | Build a process evaluator scoring path compliance | Advanced evaluator design |
| E9 | Create a failure taxonomy and classify 20 eval failures | Failure analysis |
| E10 | Configure tiered gates (Critical/block, High/must-pass, Medium/warn, Info/report) with must-pass cases and failure budgets | Release engineering |
| E11 | Document a feedback loop that converts flagged interactions to test cases | Continuous improvement |

---

## Progression Summary

```
L100: "I can run an evaluation and explain why a failure blocks release."
       │
       ▼
L200: "I can customize evaluations for my own agent and diagnose failures."
       │
       ▼
L300: "I can operationalize evaluation pipelines and govern releases at scale."
```

---

## 60-Minute Workshop Journey

For instructor-led delivery or time-boxed self-paced sessions:

| Time | Activity | Level |
|---|---|---|
| 0–5 min | Intro: why agent evaluation is different | L100 |
| 5–15 min | Run baseline evaluation (offline bundle or live demo) | L100 |
| 15–25 min | Inspect a trace, find the gate-blocking failure | L100 |
| 25–35 min | Add a deterministic evaluator for a new requirement | L200 |
| 35–45 min | Break the agent, watch the gate fail | L200 |
| 45–55 min | Discuss severity tiers and production feedback loops | L300 |
| 55–60 min | Wrap-up: map to your own scenario | All |

---

## Workshop Delivery Modes

| Mode | L100 | L200 | L300 |
|---|---|---|---|
| **Self-paced** | ✓ All content | ✓ All exercises | ✓ All exercises |
| **60-minute workshop** | 25 min (run + interpret) | 20 min (customize) | 10 min (discuss) |
| **Instructor-led (half-day)** | 45 min hands-on | 90 min hands-on | — |
| **Instructor-led (full-day)** | 45 min hands-on | 90 min hands-on | 90 min hands-on |
| **Executive briefing** | 20 min (demo only) | — | — |
