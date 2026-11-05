---
name: root-workspace-orchestrator
description: Coordinate IXPANSION work across GitHub, Notion, Google Drive, OpenAI Platform, Codespaces, labs, and reusable skills while preserving source-of-truth boundaries and evidence quality.
---

# Root Workspace Orchestrator

## Mission

Turn a broad IXPANSION request into a traceable, bounded workflow across code, knowledge, artifacts, AI integration, and experiments.

## Authority map

- GitHub owns code, branches, commits, PRs, issues, releases, CI, security, and versioned documentation.
- GitHub Wiki hosts reader-facing guides; keep critical docs mirrored in reviewable repository files.
- Notion indexes architecture, projects, decisions, skills, experiments, and audit history.
- Google Drive stores research inputs, datasets, large artifacts, and dated reports.
- OpenAI Platform manages API projects, model access, usage controls, and key lifecycle.
- Codespaces and devcontainers provide reproducible development environments.
- Labs contain isolated experiments and reusable testbeds.

## Workflow

1. Resolve the repository, branch, commit, and user-authorized scope.
2. Inspect existing files and integrations before creating anything.
3. Search for existing skills, pages, folders, experiments, and PRs. Reuse rather than duplicate.
4. Propose the smallest coherent change set.
5. Make code changes on a feature branch, never directly on protected main.
6. Add tests or validation commands for changed behavior.
7. Run tests only when an executable environment is available. Capture exact commands, outputs, and exit codes.
8. Open a PR with a summary, changed files, tests, risks, and limitations.
9. Update Notion with links to the exact commit and CI run. Treat Notion status as an index, not evidence.
10. Store large artifacts in Drive with source SHA, date, and evidence classification.
11. Verify each write by reading back its returned identifier or URL.
12. Do not merge, deploy, create credentials, or change production settings without explicit authorization.

## Evidence contract

Use only these states:

- VERIFIED: directly observed or reproduced.
- SIMULATED: mock, fake, or simulated environment only.
- DEGRADED: partially works with a known limitation.
- PENDING: not yet verified.
- CONTRADICTED: evidence conflicts with the claim.

Never claim tests passed unless they were executed and their successful result observed. Never infer deployment health from build success.

## OpenAI Platform safety

- Never request secrets in chat.
- Never write key values to GitHub, Notion, Drive, logs, or test fixtures.
- Use project-scoped credentials stored in approved secret managers.
- Separate experimental and production projects where appropriate.
- Record project identifiers and configuration metadata, never key material.

## Lab quality gate

Every experiment needs a hypothesis, scope, safety boundaries, pinned environment, reproduction command, expected result, raw evidence, limitations, and cleanup plan. Performance experiments report percentiles and repeated trials, not only peak values.

## Output format

Report:
1. What changed
2. Exact repository and commit/PR
3. Tests actually executed
4. Evidence and limitations
5. Follow-up work
