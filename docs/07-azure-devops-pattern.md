# Azure DevOps Pipeline Pattern

Use an Azure Resource Manager service connection configured for workload identity federation. The pipeline stages mirror GitHub Actions: offline validation on every pull request, credential-dependent Foundry evaluation in an approved environment, pre-release gate evaluation, and evidence publication.

Do not store client secrets, API keys, endpoints, or connection strings in YAML. Reference variable groups or environment-scoped non-secret configuration, use approval checks for live evaluation, and grant only the Foundry roles empirically validated by the live spike. Publish JSON, Markdown, JUnit, and failed traces with organization-approved retention; use 30/90 days as the starter defaults.

The Azure DevOps pattern is documentation-only in this kit. GitHub Actions is the runnable reference implementation.
