---
name: integration-smoke-testing
description: 'Exercise IXPANSION workflows across module boundaries. Use when validating API, CLI, dashboard, compose, runtime, federation, or end-to-end behavior after a change.'
argument-hint: '[workflow or changed surface]'
user-invocable: true
---

# Integration Smoke Testing

Prove that the smallest real workflow still crosses its boundaries correctly.

## Workflow

1. Choose one representative user workflow and its expected observable result.
2. Prepare deterministic local inputs with no real credentials or external effects.
3. Exercise the route, command, runtime, or compose boundary using the repository's test tools.
4. Check exact outputs, status codes, exit behavior, state changes, and audit evidence.
5. Exercise one malformed or unavailable dependency case.
6. Report environment limits separately from product failures.

## Safety boundaries

- Prefer in-process tests and local smoke checks over network-dependent tests.
- Do not use production credentials or destructive external actions.
- Keep simulated and live transport results distinct.
- Reuse existing fixtures and test commands.

## Report

Return: workflow exercised, setup, expected versus actual result, failure case,
commands, and environment limitations.
