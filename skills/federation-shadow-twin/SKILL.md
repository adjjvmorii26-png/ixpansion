---
name: federation-shadow-twin
description: Use when comparing an existing connector route with a candidate adapter using identical deterministic fixtures and differential output analysis before live rollout.
---

# Federation Shadow Twin

## Mission
Compare a known route and a candidate route under identical inputs. Find behavioral drift without production writes or real credentials.

## Required inputs
Baseline and candidate identifiers, exact source revisions, capability contract, deterministic fixture set, normalization rules, allowed environment, and finite execution budget.

## Procedure
1. Verify both route identities and revisions. Unknown identity blocks comparison.
2. Map inputs, outputs, invariants, error classes, retry behavior, and side-effect boundaries.
3. Reuse or generate synthetic valid, boundary, invalid, duplicate, stale, and adversarial fixtures.
4. Execute both routes against identical fixtures in an isolated runner. Prefer fake transports; live checks are limited to explicitly authorized read-only preflights.
5. Normalize only volatile metadata. Never normalize away permission decisions, object identity, content, or error semantics.
6. Compare schemas, values, error classification, idempotency behavior, evidence completeness, and latency when measurable.
7. Inject bounded faults: permission denial, 429, timeout-before-write, timeout-after-write, duplicate delivery, stale revision, malformed response, and readback mismatch.
8. Audit for forbidden network calls, live writes, credential access, and filesystem escape.
9. Preserve each mismatch as a minimized regression fixture.
10. Stop at CANDIDATE or BLOCKED. Live rollout is a separate approval.

## Verdicts
EQUIVALENT, DRIFTED, INCOMPLETE, BLOCKED, or NOT_RUN.

## Output
Return exact revisions, fixture-set identity, per-case comparisons, mismatches, fault results, side-effect audit, uncovered criteria, residual risks, and next safe step. Synthetic equivalence is not live provider compatibility.
