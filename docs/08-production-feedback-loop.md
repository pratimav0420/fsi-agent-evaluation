# Production Feedback Loop

1. Sample interactions using customer-approved telemetry and retention policies.
2. Remove or replace customer identifiers before evaluation work begins.
3. Triage signals by requirement and root-cause category.
4. Create a candidate case containing the minimum reproducible synthetic context.
5. Require domain and risk-owner review.
6. Promote accepted cases to adversarial or regression tiers.
7. Run the full pre-release gate and retain evidence.

The repository does not deploy monitoring, copy production data, or automate approval. It documents a governance pattern that customers adapt to their own controls.
