# 60-Minute Workshop: From Demo to Release Evidence

## Preparation

Install Python 3.11+, install the package with development dependencies, and run `fsi-agent-eval validate`. No Azure access is required for the core workshop.

## Agenda

| Time | Activity | Evidence |
|---|---|---|
| 0-5 | Introduce the post-FNOL boundary and a retrieval-before-authorization failure | Scenario contract |
| 5-12 | Explain taxonomy, Critical controls, and why scores cannot average them away | Requirements and gate docs |
| 12-20 | Run `fsi-agent-eval baseline` | JSON, Markdown, JUnit |
| 20-30 | Run `fsi-agent-eval broken`; inspect the failed trajectory | Failed gate and trace |
| 30-40 | Add or inspect one requirement-linked case; run `validate` | Traceability result |
| 40-49 | Run the 20-case pull-request profile and compare good/broken evidence | Comparison JSON |
| 49-55 | Review versions, findings, and retention in the evidence pack | Release evidence |
| 55-60 | Map the pattern to a customer scenario and capture feedback | Mapping worksheet |

## Core commands

```text
fsi-agent-eval validate
fsi-agent-eval baseline --output artifacts/baseline
fsi-agent-eval broken --output artifacts/broken
fsi-agent-eval compare
fsi-agent-eval replay --bundle data/offline-bundle/live-pass.json
```

## Instructor acceptance

The learner can identify tool order in a trace, explain why a Critical failure blocks, distinguish an agent failure from an evaluator error, and name the next artifact needed to adapt the pattern.
