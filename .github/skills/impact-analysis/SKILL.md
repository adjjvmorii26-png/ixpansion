---
name: impact-analysis
description: 'Assess the regression surface of an IXPANSION change. Use when modifying shared helpers, configuration, dependencies, public contracts, generated behavior, or cross-module workflows.'
argument-hint: '[files, symbol, or proposed change]'
user-invocable: true
---

# Impact Analysis

Estimate what can change before editing a shared surface.

## Workflow

1. Identify direct callers, tests, configuration inputs, and user-facing outputs.
2. Separate behavior changes from documentation, formatting, and metadata changes.
3. Check compatibility risks for API payloads, CLI options, imports, and defaults.
4. Identify security, offline, persistence, and deployment implications.
5. Rank risks by likelihood and consequence.
6. Select the narrowest regression checks that cover the highest risks.

## Rules

- Use source and tests as evidence; do not infer usage from names alone.
- Preserve unrelated user changes in a dirty worktree.
- Do not broaden a fix to unrelated failures.
- Treat undocumented behavior as a risk, not permission to change it silently.

## Output

Return: affected callers, compatibility risks, risk ranking, required checks,
and explicitly unaffected areas.
