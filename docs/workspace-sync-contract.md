# Workspace Nervous System v1

**Status:** implementation proposal on `feat/workspace-nervous-system-v1`; provider adapters are not yet wired to live credentials or production services.

## Why this exists

The IXPANSION workspace already has canonical Notion pages, Google Drive Shared Drive folders, a Sheets artifact registry, and GitHub as the implementation authority. This package adds the missing durable handoff primitive: an idempotent local outbox with leases, bounded retries, and mandatory destination read-back.

It deliberately does not embed Google or Notion credentials, call provider APIs, or pretend a plugin connection is a production daemon.

## System topology

```text
GitHub source / CI ─┐
Notion decisions ───┼──> Change detector ──> deterministic event key
Drive artifacts ────┘                           |
                                                v
                                      SQLite durable outbox
                                                |
                                   claim + lease + retry policy
                                                |
                               injected Notion / Drive adapters
                                                |
                                      destination read-back
                                                |
                               verified receipt + append-only run
```

## Authority boundaries

| Data | Canonical authority | Cross-system behavior |
|---|---|---|
| Code, tests, CI, PRs, releases | GitHub | Store commit and run references elsewhere |
| Decisions, skill intent, task state | Notion | Store durable artifact links and source revisions |
| Reports, exports, datasets, evidence | Google Drive | Keep immutable versions; index metadata in Notion/Sheets |
| Artifact index and reconciliation view | Google Sheets | Pointer only; not the artifact itself |
| Live provider state | Respective provider | Fetch before claiming current status |

## Event contract

Each event has:
- Stable `idempotency_key` (source ID + source revision/hash + destination + operation).
- Source, target, operation, and structured payload.
- Explicit `idempotent` flag.
- Payload SHA-256 hash.
- State: `pending`, `inflight`, `delivered`, or `dead`.
- Attempt count, lease expiry, next retry time, and redacted last error.

A duplicate key with the same operation and payload is a no-op. A duplicate key with different content is a hard conflict.

## Recovery model

- Atomic `BEGIN IMMEDIATE` claim prevents two workers from claiming the same pending event.
- A lease bounds worker ownership.
- Expired idempotent leases return to pending.
- Expired non-idempotent leases become dead because the remote side effect may have happened.
- Only explicitly transient errors on idempotent operations receive bounded exponential backoff.
- Unclassified errors, permanent errors, missing adapters, and failed read-back verification are dead-lettered.
- Dry-run previews due work without claiming or mutating it.

## Adapter contract

An adapter implements:
- `deliver(event) -> receipt`: perform a deterministic upsert or provider-supported idempotent write.
- `verify(event, receipt) -> bool`: fetch the destination and prove that the expected artifact ID, source revision/hash, and link exist.

A successful provider write response is not verification. The runner marks an event delivered only after the adapter's read-back succeeds.

## Security and privacy

- Credential-like payload keys are rejected recursively.
- Error text is redacted for common bearer and key/value token patterns.
- Provider SDKs and secrets are not imported by this package.
- No external sharing, permission mutation, deletion, merge, or deployment is performed by the outbox.
- Use least-privilege connector scopes and keep raw sensitive provider responses out of logs.

## Integration sequence

1. Build a read-only Notion/Drive/GitHub inventory adapter using the connected plugins.
2. Add deterministic source fingerprints and change detection.
3. Route Drive file metadata and Notion page pointers through the outbox.
4. Add provider-specific idempotent upsert + read-back implementations.
5. Add append-only Notion run records and Drive evidence snapshots.
6. Run shadow mode before enabling writes; compare proposed operations with observed provider state.
7. Enable one destination and one artifact type at a time.
8. Add scheduled execution only after connector identity, retry semantics, and recovery behavior are proven.

## Validation

Focused test command:

```bash
python -m unittest discover -s tests -p 'test_workspace_sync_outbox.py' -v
```

Repository suite:

```bash
python -m pytest tests/ -q --tb=short
```

These commands are instructions until executed by a real test runner. CI results are authoritative for the branch once observed.

## Related assets

- [Notion Root Workspace](https://app.notion.com/p/40f60373699681ecbae7c65216b941fa)
- [Notion Workspace Intelligence Orchestrator](https://app.notion.com/p/414603736996816eb8b8c21eaa0a5c85)
- [Google Drive Root Workspace](https://drive.google.com/drive/folders/1Ey_Al_JOVpwQnj7rN4xeKfKlG_DOoE11)
- [Google Sheets Cross-System Artifact Registry](https://docs.google.com/spreadsheets/d/1pmDFsMEdO76bU3XiG5kKMglLtGpBdg2E08sqGOAHoMQ/edit)
- [GitHub implementation branch](https://github.com/adjjvmorii26-png/ixpansion/tree/feat/workspace-nervous-system-v1)
- [Portable Gem seed](../gems/workspace-nervous-system/GEM.md)
- [Reusable operator skill](../skills/r1/workspace_nervous_system/SKILL.md)
