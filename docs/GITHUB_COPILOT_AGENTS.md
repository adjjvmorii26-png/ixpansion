# GitHub AI · Copilot agents for IXPANSION

Reference: [GitHub AI features](https://github.com/features/ai) · [Copilot agents](https://github.com/features/copilot/agents)

## What this enables

| Surface | Use on IXPANSION |
|---------|------------------|
| **Copilot in VS Code** | Inline + Chat (wired via `.vscode/` pack) |
| **Copilot coding agent** | Assign an **Issue** to Copilot → get a PR back |
| **Copilot Autofix** | Security alerts → suggested patches (GHAS) |
| **GitHub MCP** | External agents via [MCP server](https://github.com/github/github-mcp-server) |

## Install / enable (one-time, on your account)

1. Open [GitHub Copilot](https://github.com/features/copilot) and ensure your plan is active.
2. For **Coding Agent** on this repo: repo **Settings → Copilot** (or org settings) → allow coding agent / GitHub App as required by current GitHub UI.
3. Mobile: the GitHub AI / github-app deep link installs the GitHub app; desktop is enough for agent PRs.

Account billing and app install can only be completed by you — not by CI.

## Assign work to Copilot (agent loop)

1. Create an issue with a **clear acceptance checklist** (wave number, files, tests).
2. Assign the issue to **Copilot** (when enabled on the repo).
3. Copilot opens a branch + PR; review with dual-track rules.
4. Merge only when organism gates are green (lab smoke / council-smoke / targeted pytest).

### Issue template sketch

```markdown
## Goal
Add wave770_… with handler / coherence_vitals / resonates_with.

## Acceptance
- [ ] api/wave770_….py compiles
- [ ] tests/test_wave770_….py passes
- [ ] No payload leaks; silence surface if caption organ
- [ ] Lab-scoped PR; does not require full monorepo soak

## Context
Read .github/copilot-instructions.md and AGENTS.md.
```

## Repo files that guide agents

- `.github/copilot-instructions.md` — always-on agent context
- `AGENTS.md` — wave pattern + CI rules
- `docs/VSCODE_COPILOT_SETUP.md` — editor setup
- `make council` — AEGIS · HELIX · QUILL posture

## Keep on track

```bash
git pull origin main
make council
make dashboard
```

Caption: `github-ai · copilot-agent · dual-track · council`
