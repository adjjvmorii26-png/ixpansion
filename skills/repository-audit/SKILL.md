---
name: ixpansion-repository-audit
description: Evidence-based repository and pull-request audit with prioritized findings and reproducible checks.
---

# Repository Audit

1. Confirm repository identity, default branch, permissions, and current commit.
2. Inventory languages, manifests, workflows, tests, deployment configuration, and security-sensitive code.
3. Inspect open PRs before proposing overlapping changes.
4. Run static checks and focused tests when execution is available.
5. Report findings with file/line, severity, impact, evidence, and proposed remediation.
6. Separate observed facts from inferred risks and recommendations.
7. Use a named feature branch; do not modify protected branches directly.
8. Re-run tests after meaningful patches and capture actual output.
9. Prepare a PR; do not merge without explicit approval.
