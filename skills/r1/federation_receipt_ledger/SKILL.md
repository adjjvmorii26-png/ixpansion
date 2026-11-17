---
name: federation-receipt-ledger
description: Record and verify append-only lifecycle evidence for IXPANSION federated executions without duplicating outbox state.
---

# Federation Receipt Ledger Operator

## Operating sequence

1. Keep queue state in `WorkspaceOutbox`. Do not build a second dispatcher, lease manager, or retry scheduler.
2. Append lifecycle facts to `ReceiptLedger` using the same stable execution ID across the event sequence.
3. Use only the event vocabulary supported by the ledger: enqueued, claimed, dispatched, retry_scheduled, lease_expired, delivery_verified, delivery_unverified, dead_lettered, receipt_recorded, contradicted.
4. Store only bounded scalar metadata such as outbox event ID, attempt number, provider status code, or verifier identifier. Never store payloads, credentials, raw provider responses, or personal data.
5. Attach an `EvidenceReceipt` only to a `receipt_recorded` event, and only when its execution ID matches.
6. Run `verify_chain()` after import, restore, suspected corruption, or before producing an audit summary.
7. Preserve PENDING when independent verification is absent. Never infer VERIFIED from a hash-chain pass or a successful outbox state transition.
8. For stronger authenticity, anchor periodic ledger head hashes outside the database under separate administrative control.

## Interpretation

- `verify_chain() == valid` means stored events are internally consistent and append-ordered.
- It does not prove that an event was emitted by an authorized actor or that a provider action occurred.
- SQLite triggers discourage accidental mutation but are not a security boundary against a database administrator.
- The outbox remains the operational source of truth; this ledger is the forensic timeline.
