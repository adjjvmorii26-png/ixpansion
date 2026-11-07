---
name: plugin_adapter_contract
description: Specify, inspect, and validate reusable adapters for connected plugins and external services.
---

# Plugin Adapter Contract

## Capabilities
- `plugin:inspect` — inspect connection, permission, and capability state.
- `plugin:validate` — validate an adapter against the shared contract.
- `plugin:verify` — verify a read or write operation and return evidence references.

## Roots
| Root | Path |
|---|---|
| Repository | `.` |
| Registry | `.workbench/plugin-registry.yaml` |
| Adapter documentation | `docs/PLUGIN_CAPABILITY_MATRIX.md` |
| Skills | `skills/r1/` |

## Rules
- Separate read capabilities from write capabilities.
- Fail closed when connection or permission state is unknown.
- Normalize provider errors without discarding request IDs.
- Retry only idempotent operations with bounded backoff.
- Preserve pagination cursors and detect incomplete listings.
- Redact credentials and unnecessary personal data from logs.
- Classify side effects: read, reversible write, destructive write, production change.
- Require explicit approval for destructive writes, sharing/access changes, schema/data mutations, merges, and production deployments.
- Return structured outcomes: verified, failed, blocked, skipped, not_run, unverified.

### plugin:inspect
Inspect the target provider's active connection, accessible identity, scopes, and advertised capabilities. Do not infer authentication from tool availability.

### plugin:validate
Check required metadata: id, display_name, version, provider, connection_state, capabilities, read_scopes, write_scopes, approval_class, idempotency, pagination, verification, evidence_sink.

### plugin:verify
For reads, capture the returned resource identity and freshness. For writes, perform read-after-write verification where supported. An accepted API response alone is not proof of the final state.
