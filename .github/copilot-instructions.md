# IXPANSION Workspace Workflow

For complex, cross-module, user-facing, security-sensitive, or externally effectful work, apply the `workflow-force` skill before implementation. Use its sequence and completion gate; delegate specialist checks to the existing IXPANSION agents when their domain is affected.

For a simple question, focused diagnosis, or single-file change with a clear owner, use the smallest relevant workflow and validation instead of expanding the task unnecessarily.

Use [.github/skills/README.md](skills/README.md) as the human-readable index of available skills and their recommended order.

Always:

- Establish the behavior, acceptance criteria, and execution boundary before editing.
- Inspect the owning implementation and neighboring tests before changing behavior.
- Keep offline and simulated paths deterministic when credentials or network access are absent.
- Preserve public contracts unless a change is required and documented.
- Bound retries, budgets, external effects, and autonomous decisions.
- Never expose secrets or bypass authorization, trust thresholds, human gates, or URL allowlists.
- Validate focused behavior immediately after edits, then widen checks according to risk.
- Report evidence, limitations, and simulated or process-local behavior honestly.
- Preserve unrelated user changes and never commit, push, reset, create branches, or open pull requests unless explicitly requested.
