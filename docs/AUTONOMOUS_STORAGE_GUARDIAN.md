# Autonomous Storage Guardian

## Purpose

The storage guardian gives IXPANSION an independent storage-health observer. It
classifies configured backends, inspects local SquirrelCache read-only, and
emits safe remediation guidance. It is not a second storage engine and does not
claim configuration proves reachability or durability.

## Operating contract

- HEALTHY_CONFIGURED means a durable backend's required configuration exists.
  It does not mean a remote read/write/read-back probe succeeded.
- DEGRADED means only ephemeral or cold-archive storage is available, or cache
  integrity needs attention.
- BLOCKED means a durable backend's paired configuration is invalid.
- backend_reachability remains NOT_PROBED until an authenticated end-to-end
  probe can safely run with an approved test key and namespace.
- Reports never include provider URLs, tokens, or stored values.

## Autonomy boundary

The guardian is currently observe-and-recommend only. It may be scheduled by a
runtime supervisor and its reports may drive alerts or proposed repairs. It
may not rotate credentials, modify provider settings, delete durable data,
migrate authentication state, or claim a repair succeeded without read-back
evidence.

## Next evolution

1. Add an isolated, namespaced read/write/read-back probe with an idempotent
   test key and explicit provider capability declaration.
2. Add atomic primitives (increment, compare_and_swap, append_event) to the
   durable-store contract before migrating auth or state-machine callers.
3. Add a scheduled supervisor that stores signed health reports and opens
   deduplicated incidents on state transitions.
4. Add restore drills against disposable fixtures before any production restore.

## Run

    python -m api.storage_guardian
    python -m unittest tests.test_storage_guardian -v
