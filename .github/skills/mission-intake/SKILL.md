---
name: mission-intake
description: 'Turn an ambiguous IXPANSION request into a bounded mission. Use when requirements, acceptance criteria, scope, risks, stakeholders, or execution boundaries are unclear.'
argument-hint: '[request or desired outcome]'
user-invocable: true
---

# Mission Intake

Convert the request into an actionable, testable mission before implementation.

## Workflow

1. State the desired outcome in one sentence.
2. Identify inputs, outputs, users, affected modules, and acceptance criteria.
3. Mark the execution boundary as read-only, simulated, local, or externally effectful.
4. Record explicit non-goals, safety constraints, and unresolved assumptions.
5. Choose the smallest validation that could disconfirm the interpretation.
6. Return a short mission brief for the implementing agent.

## Rules

- Prefer observable behavior over implementation language.
- Preserve offline behavior when credentials or network access are absent.
- Do not invent requirements from architecture plans or comments alone.
- Escalate only decisions that change scope, public contracts, or external effects.

## Output

Return: outcome, acceptance criteria, affected surfaces, execution boundary,
non-goals, assumptions, risks, and the first discriminating check.
