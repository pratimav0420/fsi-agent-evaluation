# ADR-003: Requirement and Case Schemas

## Status

Accepted

## Decision

Requirements and curated cases are stored as validated YAML. Requirements use stable `FSI-*` IDs and include normative and operational metadata. Cases link one or more requirement IDs and define entitlement context, expected and prohibited tool behavior, escalation, oracle methods, and retained evidence.

The CLI validation command rejects duplicate or unknown IDs, empty requirement/oracle links, an incorrect case count, or a distribution other than 5/5/5/3/2.
