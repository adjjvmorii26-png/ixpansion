---
name: workspace-nervous-system
description: Build, operate, and audit IXPANSION's governed Notion, Google Drive, Google Sheets, and GitHub synchronization. Use when indexing artifacts, creating evidence handoffs, reconciling workspace state, or debugging connector drift.
---

# Workspace Nervous System

Coordinate the IXPANSION workspace as a governed, recoverable system. This skill is an operating procedure, not a permission grant.

## Authority model

- Notion: canonical instructions, decisions, task state, skill intent, and human-readable project indexes.
- Google Drive: durable reports, exports, datasets, snapshots, and evidence files.
- Google Sheets: cross-system artifact index and machine-readable reconciliation summaries.
- GitHub: executable code, tests, CI, PRs, and releases.
- Composio connectors: operational adapters to provider APIs. A connected plugin is not proof that every scope or operation is authorized.

Never mirror secrets, OAuth tokens, private keys, or bearer credentials into any system.

## Capabilities

- `workspace-sync:discover` — resolve authoritative source IDs and existing destinations before writing.
- `workspace-sync:preflight` — verify connector identity, scope, resource ownership, and operation risk.
- `workspace-sync:plan` — create deterministic artifact keys and a dry-run plan.
- `workspace-sync:enqueue` — place idempotent work into the durable SQLite outbox.
- `workspace-sync:deliver` — dispatch only through explicitly injected provider adapters.
- `workspace-sync:verify` — read the destination back and compare expected metadata/hash.
- `workspace-sync:reconcile` — classify missing, stale, duplicate, or conflicting records.
- `workspace-sync:recover` — resume expired idempotent leases; quarantine uncertain non-idempotent outcomes.
- `workspace-sync:record` — append evidence to Notion and link the Drive artifact.

## Roots

| Surface | Canonical location |
|---|---|
| Repository | `adjjvmorii26-png/ixpansion` |
| Notion root | [IXPANSION Root Workspace](https://app.notion.com/p/40f60373699681ecbae7c65216b941fa) |
| Notion Skills Lab | [IXPANSION Skills Lab](https://app.notion.com/p/40f60373699681418569f1e457572a71) |
| Drive root | [IXPANSION Root Workspace](https://drive.google.com/drive/folders/1Ey_Al_JOVpwQnj7rN4xeKfKlG_DOoE11) |
| Artifact registry | [Cross-System Artifact Registry](https://docs.google.com/spreadsheets/d/1pmDFsMEdO76bU3XiG5kKMglLtGpBdg2E08sqGOAHoMQ/edit) |

## Workflow

1. DISCOVER: search Notion, the correct Google Shared Drive, and GitHub. Reuse existing pages/folders/files. Do not infer emptiness from a My Drive-only search when the target is in a Shared Drive.
2. RESOLVE: record exact page/database IDs, Drive file/folder IDs, repository/ref, and provider account. Read Notion database schemas before creating rows.
3. PREFLIGHT: confirm active connector, intended account, permission scope, and supported tool operation.
4. PLAN: derive a stable idempotency key from source system, source object ID, source revision/hash, destination, and operation. Produce a non-mutating dry run.
5. CLASSIFY: read-only and reversible metadata writes may proceed when authorized. Ask before destructive changes, external sharing, permission changes, merges, deployments, or irreversible operations.
6. ENQUEUE: persist the event to `integrations/workspace_sync/outbox.py`. Reject credential-like payload fields. A repeated key with identical content is a no-op; a repeated key with changed content is a conflict.
7. DELIVER: use the relevant connected plugin adapter. Provider writes must accept an idempotency key or use a deterministic upsert. Do not retry non-idempotent writes after an uncertain outcome.
8. VERIFY: read the destination back. Compare stable IDs, source revision, content hash, and expected links. A successful write response alone is not verified.
9. RECORD: append a dated run record in Notion and link the Drive artifact. Preserve raw evidence in Drive when useful; never overwrite historical evidence.
10. REPORT: distinguish VERIFIED, PARTIAL, UNKNOWN, BLOCKED, NOT RUN, FAILED, and UNVERIFIED. Never convert missing data into zero or claim an unexecuted test.

## Failure policy

- 401/403: check account identity and scopes; do not silently switch identities.
- 404: distinguish missing resource from wrong workspace/team/Shared Drive scope.
- Rate limit/transient network error: retry only idempotent operations with bounded backoff.
- Expired idempotent lease: safe to requeue.
- Expired non-idempotent lease: mark outcome uncertain and quarantine for reconciliation.
- Read-after-write mismatch: do not mark delivered; preserve the failure evidence.
- Connector outage: isolate that adapter and continue independent read-only work where safe.

## Verification commands

From repository root:

```bash
python -m unittest discover -s tests -p 'test_workspace_sync_outbox.py' -v
python -m pytest tests/ -q --tb=short
```

The first command is the focused local contract test. The second is the repository-wide CI-equivalent suite. Do not report either as passed until it is actually run.

## Examples

### workspace-sync:plan
Create a dry-run plan for a GitHub commit receipt to be indexed in Notion and archived in Drive. Resolve the exact source SHA, existing Notion page, and Drive destination. Derive one idempotency key per destination operation. Do not write.

### workspace-sync:enqueue
Enqueue a Notion artifact-pointer upsert with a stable key and a payload containing only artifact ID, source SHA, timestamp, evidence state, and destination link. Reject credential-like fields.

### workspace-sync:verify
After a provider adapter reports success, fetch the exact destination record and compare its stable ID and source SHA. Mark delivered only if the read-back matches.

### workspace-sync:reconcile
Compare the Notion index, Drive artifact metadata, and GitHub source revision. Emit missing/stale/conflict classifications; never silently choose a winner when two canonical sources disagree.
