---
name: connector-chaos-simulator
description: Use when testing connector resilience with deterministic fake-provider failures such as rate limits, timeouts, duplicate delivery, malformed responses, stale reads, and partial fan-out.
---

# Connector Chaos Simulator

## Mission
Exercise connector failure handling in a local fake-provider harness. This is controlled reliability testing, not live fault injection.

## Safety boundary
- Use fake transports and synthetic data only.
- Never throttle, corrupt, interrupt, or overload real providers.
- Never use production credentials or customer data.
- Stop if the harness cannot prove that requests are intercepted locally.

## Scenario catalogue
- AUTH_EXPIRED and PERMISSION_DENIED.
- RATE_LIMIT with retry-after values and bounded backoff.
- TIMEOUT_BEFORE_WRITE and TIMEOUT_AFTER_WRITE.
- DUPLICATE_EVENT and SAME_KEY_DIFFERENT_PAYLOAD.
- STALE_READ and EVENTUAL_CONSISTENCY_DELAY.
- MALFORMED_JSON, INVALID_UTF8, oversized response, and schema drift.
- PARTIAL_FANOUT with one destination succeeding and another failing.
- READBACK_MISMATCH and unknown remote outcome.

## Procedure
1. Pin the adapter revision, fake transport, fixture seed, and scenario budget.
2. Establish a clean baseline and prove all outbound calls are intercepted.
3. Execute one scenario at a time with deterministic scheduling.
4. Assert retry limits, idempotency behavior, quarantine rules, and accurate operation states.
5. Verify unknown outcomes are read back before retry; non-idempotent unknowns must quarantine.
6. Verify partial fan-out preserves successful legs and retries only safe failed legs.
7. Check that logs contain no secrets and that no real provider endpoint was contacted.
8. Preserve failures as regression fixtures and report untested scenarios.

## Output
Return scenario matrix, exact run identity, retry and quarantine observations, partial-fanout ledger, outbound-call audit, failures, and PASS, FAIL, BLOCKED, or NOT_RUN. Fake-provider success is not live provider proof.
