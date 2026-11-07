---
name: ixpansion-plugin-adapter-contract
description: Design and validate reusable adapters for connected plugins and external services.
---

# Plugin Adapter Contract

Every integration is an adapter behind a stable capability interface.

Required metadata: id, display_name, version, provider, connection_state, capabilities, read_scopes, write_scopes, approval_class, idempotency, pagination, rate_limit_notes, verification, evidence_sink.

Required behavior:
- Fail closed when connection state or permissions are unknown.
- Separate read and write operations.
- Normalize provider errors without discarding request IDs.
- Retry only idempotent operations with bounded backoff.
- Preserve pagination cursors; never silently truncate complete listings.
- Redact secrets and unnecessary personal data from logs.
- Return structured outcomes: succeeded, failed, blocked, skipped, not_run.
- Include evidence references for successful writes.

Capability tiers:
- Tier 0: discover and inspect.
- Tier 1: reversible drafts and branch-scoped writes.
- Tier 2: persistent data/schema changes, sharing, or access changes; approval required.
- Tier 3: merges, production deployments, destructive actions; explicit approval required.

Test disconnected state, insufficient scope, timeout, rate limiting, pagination, duplicate requests, partial failure, provider conflict, redaction, read-after-write verification, and rollback/recovery where supported.
