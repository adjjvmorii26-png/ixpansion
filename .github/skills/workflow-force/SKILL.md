---
name: workflow-force
description: 'Coordinate a disciplined IXPANSION delivery workflow across agents. Use when a request needs intake, architecture, implementation, resilience, observability, testing, or release evidence in a fixed sequence.'
argument-hint: '[mission to coordinate]'
user-invocable: true
---

# Workflow Force

Coordinate shared skills into an evidence-driven delivery loop. This skill
sets order and completion gates; it does not replace specialist judgment.

## Required Sequence

1. Run mission intake and record outcome, acceptance criteria, and execution boundary.
2. Review architecture boundaries and identify the owning implementation.
3. Analyze impact and rank compatibility, security, and operational risks.
4. Produce an implementation plan with file ownership and a first validation.
5. Implement the smallest vertical slice through the owning abstractions.
6. Add resilience and observability where the workflow has failure or decision boundaries.
7. Run focused integration smoke tests and the relevant specialist checks.
8. Reconcile evidence with source and tests; resolve contradictions at the owner.
9. Close with a release-style report of changes, validation, limitations, and follow-up decisions.

## Coordination Rules

- Parallelize only independent read-only analysis or file-disjoint work.
- Do not advance past a failed gate without recording the failure and containment decision.
- Keep offline, simulated, and externally effectful behavior clearly separated.
- Never bypass authorization, trust thresholds, human gates, budgets, or URL allowlists.
- Preserve unrelated user changes and never commit, push, reset, or open a pull request unless explicitly requested.

## Completion Gate

The workflow is complete only when the requested behavior is evidenced by
focused checks, known limitations are stated, and no unsupported capability is
reported as production-ready.

## Output

Return: mission brief, ownership and risk summary, delegated work, evidence,
safety decisions, changed surfaces, limitations, and next blocking decision.
