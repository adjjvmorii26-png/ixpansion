---
name: partial-failure-compensator
description: Use when a multi-provider workflow partially succeeds and needs safe reconciliation, retry planning, or reversible compensation.
---

# Partial Failure Compensator

## Mission
Recover from partial connector workflows without pretending multiple providers share one transaction.

## Protocol
1. Freeze dependent writes after the first failed or ambiguous provider mutation.
2. Build an operation ledger: step ID, provider, target ID, idempotency key, intended change, returned result, and readback state.
3. Classify each operation SUCCESS_CONFIRMED, FAILED_CONFIRMED, UNKNOWN, or NOT_ATTEMPTED.
4. Read back UNKNOWN operations before retrying. Never blindly replay a non-idempotent action.
5. Determine whether the failed workflow can safely resume from the last verified checkpoint.
6. Prefer forward repair when it is safer and authorized. Use compensating actions only if reversible and explicitly permitted.
7. Do not delete, revoke, overwrite, publish, merge, or deploy as an improvised rollback.
8. Re-run readback and reconcile all providers after recovery.

## Output
Return the operation ledger, confirmed state, unknown state, retry safety, proposed compensation, required approval, and final reconciliation. Report partial success honestly.
