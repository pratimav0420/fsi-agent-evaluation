# ADR-002: Evaluation Strategy

## Status

Accepted

## Decision

Use deterministic assertions for objective controls, model-based evaluators only for semantic judgment, separated suites, and one requirement-traceable report. Critical authorization and action boundaries never pass through averaging. Function-tool traces are normalized behind `AgentAdapter`; client-captured tool outputs are merged with provider step metadata when the provider does not return outputs.

## Consequences

The gate remains explainable and provider-neutral, but multiple evidence sources must be retained and evaluator infrastructure failures must be modeled separately from agent failures.
