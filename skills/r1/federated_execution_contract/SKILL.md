---
name: federated-execution-contract
description: Apply IXPANSION's shared provider policy, approval, and evidence contract before connector work.
---

# Federated Execution Contract Operator

Use this skill whenever a provider adapter proposes an action that could read, write, publish, deploy, or otherwise affect an external system.

## Required sequence

1. **Classify the action.** Choose exactly one: `read_only`, `sandbox_write`, `external_side_effect`, or `production_change`. Do not downgrade the class to avoid approval.
2. **Build the envelope.** Use `ExecutionEnvelope.build` with a stable execution ID, provider/action identifiers, idempotency key, JSON payload, and timezone-aware timestamp. Keep secrets out of payloads.
3. **Enqueue through the policy bridge.** Use `enqueue_if_authorized` with the exact envelope, policy, payload, source, target, and operation. It verifies the payload digest and evaluates provider/action allowlists before inserting into the SQLite outbox. A denial must not enqueue.
4. **Require approval where configured.** External side effects and production changes require explicit approval by default. An approval must be scoped to the exact action and target, not inferred from a general request to continue. Pass `approved=True` only after that approval exists.
5. **Execute through the outbox runner.** The bridge only enqueues; `WorkspaceSyncRunner` claims a fenced lease and invokes the injected provider adapter. Use bounded transport, provider-native idempotency where available, and destination read-back verification.
6. **Create an evidence receipt.** Bind the envelope, exact policy digest, observed timestamp, mode, verification state, and canonical result digest. Default verification to PENDING.
7. **Preserve uncertainty.** Hashes establish integrity, not truth. Do not mark evidence VERIFIED without an independent verifier and explicit verification basis. Use SIMULATED for dry-runs and DEGRADED when a required source or verification step is unavailable.
8. **Record the result.** Keep raw secrets and sensitive payloads out of Notion, Drive metadata, logs, and receipts. Store durable execution state in the outbox; use Notion for decisions and indexes, Drive for files/evidence, and GitHub for versioned code and CI.

## Hard stops

- Missing provider or action allowlist.
- Payload digest mismatch between the envelope and enqueue request.
- Secret-like fields rejected by the outbox.
- Invalid or naive timestamps.
- Oversized, non-JSON, or non-finite payloads.
- Missing approval for a gated action.
- Provider errors, ambiguous writes, failed read-back, or expired leases without a safe recovery path.
- Any request to claim a live action or verified result without provider evidence.

## What this skill does not authorize

It does not authorize merges, deployments, secret provisioning, account changes, external sharing, or production writes. It does not turn a connector's availability into permission to use it. The user must approve the exact sensitive action when the workflow requires it.
