---
name: mesh-telemetry-state-preserver
description: Designs and reviews telemetry routers and cross-repository event bridges so live, cached, simulated, stale, and degraded observations cannot be confused or silently promoted to authoritative state.
---

# Mesh Telemetry State Preserver

## Design intent

A telemetry event is an observation with a source and a time, not merely a value. Preserve its epistemic state across adapters, caches, dashboards, and repository boundaries. Optimize delivery without laundering uncertainty.

## Canonical event envelope

Use a versioned envelope with fields appropriate to the host system:

- `schema_version`: explicit, validated version.
- `event_id`: stable identity for this observation; do not derive solely from payload equality.
- `source_id`: producer identity, not a user-facing label.
- `observed_at`: producer observation time, with timezone/clock semantics.
- `received_at`: receiver time, kept distinct from observation time.
- `state`: one of LIVE, CACHED, SIMULATED, STALE, DEGRADED, or UNKNOWN.
- `payload`: domain data, validated independently.
- `provenance`: source method and transformation lineage.
- `integrity`: check performed and result; never imply truth from a hash alone.
- `expires_at` or an explicit freshness policy where the event can age out.
- `verification`: exact verifier, scope, time, and result when applicable.

Do not force all projects to adopt these literal field names without a compatibility adapter. The invariants matter more than the wire spelling.

## State invariants

- **LIVE** means the request obtained a fresh observation from the declared live source under a documented freshness policy. It does not automatically mean verified or authoritative.
- **CACHED** means the value was served from a cache. Retain original observation time and source; never relabel a cache hit LIVE.
- **SIMULATED** means synthetic or test data. It must remain visibly non-production through aggregation, exports, and alerts.
- **STALE** means freshness policy failed or cannot be established. Do not silently fall back to a green/live dashboard state.
- **DEGRADED** means partial capability, fallback, or source failure affected the observation. Include a machine-readable reason.
- **UNKNOWN** is the safe result for missing, malformed, or unsupported state values.

A transformation may degrade state, but may not upgrade trust without an explicit, independently validated rule. Examples: LIVE → CACHED is allowed when persisted and served later; LIVE → VERIFIED is not allowed merely because it was cached or hashed; SIMULATED → LIVE is forbidden.

## Router and federation checklist

1. Validate schema and state before routing.
2. Preserve source and both timestamps through serialization and caching.
3. Make TTL/freshness policy consumer-specific; a five-minute cache may be acceptable for a dashboard and invalid for a safety gate.
4. Use monotonic clocks for elapsed-time measurement where available, and wall-clock timestamps for cross-process lineage. Document clock-skew assumptions.
5. Distinguish absent data from zero, empty, false, and unknown.
6. Make fallback behavior explicit and observable; never silently switch a production feed to simulation.
7. Treat signatures, hashes, and transport authentication as different checks with different claims.
8. On schema mismatch, unknown state, verifier outage, or expiry, preserve the failure reason and degrade or reject the event.
9. Prevent duplicate delivery from becoming duplicate action: use event identity and idempotency keys at the side-effect boundary.
10. Keep secrets and sensitive payload fields out of logs; log event IDs, state transitions, reason codes, and bounded metadata instead.
11. Bound queues, retries, payload size, and cache growth. Backpressure must be observable.
12. Keep read-only telemetry separate from command/execution channels. An observation should never become an action request by shape coincidence.

## Required adversarial tests

- Cached values retain the original observation time and remain CACHED.
- Expired events cannot satisfy a fresh-data requirement.
- SIMULATED events never appear as LIVE in reports or alerts.
- Unknown/malformed state values become UNKNOWN or are rejected.
- Missing provenance cannot pass a verification gate.
- Tampered payload and tampered provenance fail independently.
- Duplicate delivery is idempotent at action boundaries.
- Source timeout produces an explicit DEGRADED state or a documented fail-closed response.
- Clock skew and boundary TTL cases behave deterministically.
- Serialization round-trips preserve state, identity, timestamps, and verification scope.
- A healthy source with a failed verifier is not represented as verified.
- A cache backend outage cannot silently switch to a less durable authoritative store.

## Output contract for a review

Report:
- event producers and consumers;
- state transition graph;
- freshness and TTL policy by consumer;
- verification and authority rules;
- fallback/degradation matrix;
- idempotency strategy;
- adversarial test coverage;
- unverified assumptions and rollout/rollback plan.

## Safe rollout

1. Observe-only instrumentation: emit state transitions without changing routing.
2. Shadow validation: compare legacy and explicit-state outputs.
3. Enforce non-upgrade invariants in a narrow adapter.
4. Add consumer-specific freshness checks.
5. Roll out across repository bridges one boundary at a time.
6. Keep rollback paths from silently converting SIMULATED or STALE into LIVE.

## Stop conditions

Do not promote an event to LIVE or VERIFIED when the source, clock policy, provenance, or verification scope is undefined. Preserve the reason for uncertainty and ask for the missing contract rather than inventing one.
