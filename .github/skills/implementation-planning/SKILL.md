---
name: implementation-planning
description: 'Plan a focused IXPANSION implementation. Use when a mission needs ordered edits, task dependencies, ownership assignments, bounded scope, or a test-backed vertical slice.'
argument-hint: '[mission or feature]'
user-invocable: true
---

# Implementation Planning

Turn an approved mission into the smallest sequence of executable edits.

## Workflow

1. Define the behavior change and its owning module.
2. List prerequisite contract, model, configuration, and test changes.
3. Order edits so each step leaves a testable state.
4. Keep one agent responsible for each file-confined slice.
5. Define the first focused validation before implementation begins.
6. Include rollback or containment behavior for partial failure.

## Safety boundaries

- Prefer existing patterns and helpers.
- Avoid speculative abstractions and unrelated cleanup.
- Keep budgets, retries, trust thresholds, and human gates explicit.
- Stop planning when the requested behavior is fully covered by the slice.

## Report

Return: ordered task list, file ownership, dependencies, first validation,
completion criteria, and known blockers.
