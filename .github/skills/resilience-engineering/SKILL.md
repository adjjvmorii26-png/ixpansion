---
name: resilience-engineering
description: 'Design and test failure handling in IXPANSION. Use when work involves retries, timeouts, partial failure, unavailable capacity, stale state, degraded mode, federation, or external services.'
argument-hint: '[failure mode or workflow]'
user-invocable: true
---

# Resilience Engineering

Make failure behavior bounded, observable, and safe to retry.

## Workflow

1. Enumerate dependency failures, malformed inputs, timeouts, stale state, and capacity loss.
2. Define the fail-open or fail-closed decision for each case.
3. Bound retries, backoff, time, work, and external calls.
4. Make writes idempotent and attach a stable task or workflow identifier when needed.
5. Preserve useful partial results without misrepresenting completion.
6. Test recovery, exhaustion, replay, and degraded operation.

## Rules

- Fail closed for unsafe URLs, invalid trust, exceeded budgets, and missing required capacity.
- Do not retry non-idempotent effects without an explicit policy.
- Keep network and credentials mocked in tests.
- Distinguish simulated recovery from real distributed guarantees.

## Output

Return: failure matrix, safety decisions, retry budget, idempotency strategy,
and focused test results.
