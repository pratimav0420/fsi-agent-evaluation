# Failure Analysis Lab

Each scenario captures the input, expected behavior, response, trajectory, evaluator result, root cause, remediation, and regression case. Start with `authorization-ordering.yaml`; the remaining catalog entries define the next intentionally broken adapters.

| Failure | Requirement | Detection |
|---|---|---|
| Authorization ordering | FSI-AUTH-001 | Entitlement-before-retrieval assertion |
| Cross-customer disclosure | FSI-PII-001 | Disclosure and protected-tool assertion |
| Wrong claim identifier | FSI-TOOL-001 | Tool argument assertion |
| Prompt injection | FSI-INJ-001 | Prohibited boundary plus semantic rubric |
| Prohibited autonomy | FSI-ACT-001 | Prohibited tool/action assertion |
| Unsupported citation | FSI-CIT-001 | Citation support evaluator |
| Tool failure masked as success | FSI-REL-001 | Error/response consistency |
| Aggregate-score masking | Gate policy | Individual Critical precedence |
