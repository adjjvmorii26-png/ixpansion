# IXPANSION Skills

Workspace skills are on-demand workflows for implementation, review, testing,
operations, security, and documentation. Use the smallest relevant skill for a
focused task. Use `workflow-force` for complex, cross-module, user-facing,
security-sensitive, or externally effectful work.

## Recommended Path

1. Start with [mission-intake](mission-intake/SKILL.md) when the outcome or scope is unclear.
2. Use [architecture-boundary-review](architecture-boundary-review/SKILL.md) and [impact-analysis](impact-analysis/SKILL.md) before cross-module changes.
3. Use [implementation-planning](implementation-planning/SKILL.md) before a multi-step edit.
4. Apply the domain skill that matches the change.
5. Use [integration-smoke-testing](integration-smoke-testing/SKILL.md) and [resilience-engineering](resilience-engineering/SKILL.md) when boundaries or failures are involved.
6. Finish with [observability-engineering](observability-engineering/SKILL.md), [python-test-engineer](python-test-engineer/SKILL.md), or [release-preparer](release-preparer/SKILL.md) as appropriate.

## Coordination

- [workflow-force](workflow-force/SKILL.md): sequence a complex mission and enforce completion evidence.
- [multi-layer-autonomous](multi-layer-autonomous/SKILL.md): coordinate bounded autonomous behavior across layers.

## Engineering

- [architecture-boundary-review](architecture-boundary-review/SKILL.md): find owning abstractions and integration boundaries.
- [impact-analysis](impact-analysis/SKILL.md): assess regression and compatibility risk.
- [implementation-planning](implementation-planning/SKILL.md): create an ordered, test-backed implementation slice.
- [observability-engineering](observability-engineering/SKILL.md): add safe diagnostics, telemetry, and audit evidence.
- [performance-capacity](performance-capacity/SKILL.md): measure bottlenecks and resource limits.
- [resilience-engineering](resilience-engineering/SKILL.md): handle retries, timeouts, partial failure, and degraded operation.

## Product Surfaces

- [api-contract-checker](api-contract-checker/SKILL.md): verify FastAPI routes, payloads, status codes, and OpenAPI behavior.
- [cli-ux-optimizer](cli-ux-optimizer/SKILL.md): improve CLI options, validation, errors, and offline behavior.
- [documentation-architect](documentation-architect/SKILL.md): keep README and usage documentation aligned with code and tests.
- [integration-smoke-testing](integration-smoke-testing/SKILL.md): exercise API, CLI, runtime, compose, and end-to-end workflows.
- [xai-integration-maintainer](xai-integration-maintainer/SKILL.md): maintain optional xAI configuration, requests, parsing, and failures.

## Quality And Safety

- [ci-pipeline-maintainer](ci-pipeline-maintainer/SKILL.md): maintain CI workflows and validation commands.
- [dependency-auditor](dependency-auditor/SKILL.md): audit dependency declarations and import failures.
- [python-test-engineer](python-test-engineer/SKILL.md): write focused Python regression and boundary tests.
- [release-preparer](release-preparer/SKILL.md): check release readiness and compatibility.
- [security-secrets-auditor](security-secrets-auditor/SKILL.md): audit secrets, configuration, URLs, and security-sensitive changes.
