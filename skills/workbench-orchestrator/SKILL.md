---
name: ixpansion-workbench-orchestrator
description: Reusable workflow for coordinating repository work, connected plugins, skills, experiments, and evidence with explicit safety gates.
---

# Workbench Orchestrator

1. Resolve exact project, repository, branch, environment, and target resources.
2. Discover connectors and inspect current schemas before unfamiliar actions.
3. Read relevant provider skills and current documentation for fast-changing services.
4. Plan with read-only discovery before writes.
5. Classify actions: read, reversible write, destructive write, production change.
6. Require explicit approval for destructive writes, merges, production deployments, sharing/access changes, and schema/data mutations.
7. Execute the smallest reversible change first; prefer branches, drafts, previews, and dry runs.
8. Run focused tests, then broader regression tests where feasible.
9. Verify by reading back changed resources or observing actual test/deployment output.
10. Append evidence; distinguish verified, failed, blocked, skipped, and not-run.

Never claim tests passed without observed execution output. Never claim production health from project existence alone. Never copy credentials into code, manifests, prompts, or logs. Never merge or deploy production without explicit approval.
