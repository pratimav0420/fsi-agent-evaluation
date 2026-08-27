# Failure Analysis Lab

The implemented authorization-ordering scenario captures the input, expected behavior, trajectory,
evaluator, root cause, remediation, and regression test. Run it with:

```text
fsi-agent-eval broken --cases evaluations/datasets/seed-cases.yaml --output artifacts/broken
```

The command is expected to exit nonzero because the critical control blocks release. The remaining
rows are candidate extensions, not implemented failure bundles.

| Status | Failure | Requirement | Detection |
|---|---|---|---|
| Implemented | Authorization ordering | FSI-AUTH-001 | Entitlement-before-retrieval assertion |
| Candidate | Cross-customer disclosure | FSI-PII-001 | Disclosure and protected-tool assertion |
| Candidate | Wrong claim identifier | FSI-TOOL-001 | Tool argument assertion |
| Candidate | Prompt injection | FSI-INJ-001 | Prohibited boundary plus semantic rubric |
| Candidate | Prohibited autonomy | FSI-ACT-001 | Prohibited tool/action assertion |
| Candidate | Unsupported citation | FSI-CIT-001 | Citation support evaluator |
| Candidate | Tool failure masked as success | FSI-REL-001 | Error/response consistency |
| Candidate | Aggregate-score masking | Gate policy | Individual Critical precedence |
