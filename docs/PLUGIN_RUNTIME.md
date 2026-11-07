# IXPANSION Plugin Runtime v1

## Design

The runtime separates provider-neutral orchestration from provider-specific connectors:

`Host authorization → Adapter registry → Policy gate → Adapter execute → Verify → Evidence ledger`

Provider credentials and sessions stay in provider-managed connector contexts. Runtime payloads must not contain credentials.

## Implemented primitives

- `PluginRegistry`: registers adapters and exposes their advertised capabilities.
- `Capability`: describes operation approval class, idempotency, and verification support.
- `PluginRuntime`: routes calls, blocks unapproved writes, retries only idempotent work, and verifies writes.
- `EvidenceLedger`: appends redacted JSONL records with deterministic evidence IDs.
- `ExecutionResult`: normalized outcome and evidence reference.

## Safety semantics

| Operation class | Approval | Retry |
|---|---|---|
| read | not required | bounded |
| reversible write | required | bounded only when idempotent |
| sensitive/destructive/production write | required; host must enforce elevated approval | bounded only when idempotent |

The runtime currently exposes generic approval classes. Production-grade host authorization, provider-specific scopes, durable ledger storage, tamper-evident chaining/signatures, and provider adapters are separate integration tasks.

## Outcome semantics

- VERIFIED: read completed or write passed adapter verification.
- SUCCEEDED: write completed but verification is not supported.
- FAILED: execution failed after allowed attempts.
- BLOCKED: policy prevented execution.
- UNVERIFIED: write returned but verification failed.
- NOT_RUN / SKIPPED: reserved for host orchestration outcomes.

## Run tests

```bash
python -m unittest tests.test_plugin_runtime -v
```

No provider API is called by these tests; they use a deterministic fake adapter.
