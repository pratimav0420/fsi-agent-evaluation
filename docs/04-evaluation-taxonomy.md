# Evaluation Taxonomy

The taxonomy uses six domains: outcome, evidence, process, control, resilience, and experience.

| Domain | Question | Typical evaluator |
|---|---|---|
| Outcome | Did the legitimate servicing goal complete? | Deterministic outcome assertion |
| Evidence | Is the answer grounded and cited? | Evidence assertion plus semantic rubric |
| Process | Were the correct tools and arguments used in a safe order? | Trajectory assertions |
| Control | Were authorization, privacy, injection, and action boundaries respected? | Deterministic must-pass controls |
| Resilience | Were faults, latency, and evaluator errors handled explicitly? | Error, timing, and completeness checks |
| Experience | Was the response clear, complete, and empathetic? | Model-based rubric |

Suites remain separate: deterministic, model-based, trajectory/process, and informational. The combined report preserves every result and applies gate precedence; it does not calculate a blended agent score.

The golden dataset contains exactly 20 curated cases: five happy paths, five boundary/ambiguity cases, five prohibited/adversarial cases, three operational failures, and two cross-customer authorization cases. Candidate, adversarial, and regression tiers are promoted through human review; LLM generation may propose candidates but never directly change release-gating data.
