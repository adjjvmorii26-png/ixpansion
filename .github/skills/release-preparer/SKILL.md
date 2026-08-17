---
name: release-preparer
description: 'Prepare an IXPANSION release or pull request. Use when reviewing branch readiness, changelog or README updates, version metadata, CI status, API compatibility, and security-sensitive configuration.'
argument-hint: '[release or pull request scope]'
user-invocable: true
---

# Release Preparer

Turn a working branch into a reviewable, reproducible change.

## Workflow

1. Inspect `git status`, the branch diff, recent history, and the default branch.
2. Separate intended changes from unrelated work; never discard user changes.
3. Verify README, `.env.example`, CLI behavior, API behavior, tests, and CI agree.
4. Run compilation, the full unittest suite, and `git diff --check`.
5. Check that no `.env`, API key, bytecode, or generated artifact is included.
6. Summarize behavior changes, validation results, compatibility risks, and any follow-up work.
7. Do not commit or create a pull request unless explicitly requested.

A release is not ready when its documented commands, configuration, or API responses disagree with the implementation.
