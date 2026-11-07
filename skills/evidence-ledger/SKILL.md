---
name: ixpansion-evidence-ledger
description: Record and verify engineering operations with provenance, redaction, and honest status semantics.
---

# Evidence Ledger

For each operation record UTC timestamp, actor, adapter/tool, target, action, input digest, outcome, verification method, evidence references, and redaction notes.

Allowed outcomes: verified, failed, blocked, skipped, not_run, unverified.

An accepted API response proves only that the API accepted the operation. For writes, perform read-after-write verification when possible. For tests, retain command, exit code, concise output, and environment identity. For deployments, distinguish deployment creation, build success, readiness, and production health.

Never log tokens, passwords, private keys, raw environment values, or unnecessary personal data. Store large logs as artifacts and link by stable reference plus digest. Do not rewrite historical evidence; append correction events that reference the original record.
