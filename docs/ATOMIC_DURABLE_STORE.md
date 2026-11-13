# Atomic Durable Store Contract

## Why this exists

Read-modify-write through generic GET/PUT is not safe for concurrent counters
or state transitions. This adapter exposes server-side atomic operations and
refuses to pretend that a generic HTTP JSON endpoint has those capabilities.

## Current implementation

The first adapter targets the configured Upstash Redis REST backend:

- `increment`: Redis `INCRBY`, atomic at the server.
- `compare_and_swap`: Redis `EVAL` script that compares the current serialized
  value (or checks that it is missing) and writes the replacement in one
  server-side operation.
- `append_event`: Redis Streams `XADD`; optional idempotency key is checked
  and recorded in the same Lua script, with a configurable deduplication TTL.

Keys are namespaced under `ixpansion:atomic:`. Event payloads are JSON encoded.
The deduplication window is bounded and therefore does not guarantee permanent
exactly-once processing after expiry.

## Failure semantics

- No Upstash configuration: capability error.
- Generic HTTP backend: capability error until it implements and advertises an
  atomic contract.
- /tmp and GitHub cold archive: never accepted for atomic operations.
- Network timeout after server execution: outcome may be unknown. Callers must
  retry with the same idempotency key where supported, or read authoritative
  state before retrying.
- A cache is never consulted by this adapter.

## Migration gates

Do not migrate auth, billing, quota, or consciousness state until:
1. A real Upstash database is configured in the target runtime.
2. Concurrency tests run against that real service.
3. Restart and timeout-after-commit behavior are tested.
4. Existing state has a verified backup and migration reconciliation plan.
5. The caller's authorization and transactional invariants are documented.

## Local tests

    python -m unittest tests.test_atomic_store -v
