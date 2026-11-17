# Federation Receipt Ledger v1

The receipt ledger adds an append-only execution history beside the Workspace Nervous System outbox. It records compact lifecycle facts without duplicating queue ownership, dispatch, retries, or provider state.

## Why a second ledger?

The outbox answers operational questions such as what is pending, inflight, delivered, or dead. The receipt ledger answers forensic questions: what sequence of lifecycle facts was recorded for an execution, what evidence receipt was attached, and whether the stored history still forms an intact chain.

## Event vocabulary

- `enqueued`
- `claimed`
- `dispatched`
- `retry_scheduled`
- `lease_expired`
- `delivery_verified`
- `delivery_unverified`
- `dead_lettered`
- `receipt_recorded`
- `contradicted`

Events contain an execution ID, UTC observation time, bounded scalar details, and optionally a compact `EvidenceReceipt`. They never contain provider payloads, credentials, or raw result bodies.

## Integrity model

Each row contains a monotonically increasing sequence, the previous row's SHA-256 hash, canonical event JSON, and its own SHA-256 hash. A SQLite transaction serializes appends. Database triggers reject ordinary UPDATE and DELETE statements. `verify_chain()` checks sequence continuity, canonical serialization, previous-hash links, and event hashes.

This is tamper-evident, not tamper-proof. A database administrator able to replace the database and triggers can rewrite the entire chain. Hashes do not prove who emitted an event, whether a provider really ran, or whether an assertion is true. For stronger authenticity, periodically anchor the ledger head hash in an independently controlled system or sign checkpoints with a separately managed key.

## Safety boundaries

- The ledger is a separate append-only audit surface; it does not dispatch work.
- The WorkspaceOutbox remains authoritative for queue state, fenced leases, retries, and recovery.
- The ledger rejects secret-like field names, bearer/access-token patterns, nested structures, and oversized string details.
- Receipts contain digests and metadata only. A receipt remains PENDING unless an independent verifier supplies a supported verification basis.
- A valid chain means internally consistent stored history, not VERIFIED execution evidence.

## Minimal use

```python
from datetime import datetime, timezone
from integrations.federation.receipt_ledger import ReceiptLedger

ledger = ReceiptLedger("var/ixpansion/federation-ledger.sqlite3")
ledger.append(
    execution_id="exec-001",
    event_kind="enqueued",
    occurred_at=datetime.now(timezone.utc),
    details={"outbox_event_id": 17},
)
assert ledger.verify_chain()["valid"]
```

## Validation

Tests cover lifecycle ordering, receipt-to-execution binding, secret/detail rejection, append-only SQL guards, tamper detection, and concurrent appends. The implementation must remain untrusted until CI validates the exact branch head.
