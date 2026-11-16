# Federated Execution Contract v1

The shared execution contract gives provider adapters one deterministic vocabulary for describing an action, checking authority, and recording a compact evidence receipt.

## Components

- `ExecutionEnvelope`: immutable action identity, provider/action names, action class, idempotency key, canonical payload digest, payload byte count, and UTC creation time.
- `ExecutionPolicy`: provider/action allowlists, payload bound, attempt ceiling, lease TTL, and action classes that require explicit approval.
- `PolicyDecision`: stable allow/deny result and the digest of the exact policy evaluated.
- `EvidenceReceipt`: execution identity, provider/action, observation time, LIVE/SIMULATED/DEGRADED mode, VERIFIED/PENDING/CONTRADICTED/STALE state, and policy/payload/result digests.

## Default authority model

| Action class | Default approval |
|---|---|
| read_only | Not required |
| sandbox_write | Not required |
| external_side_effect | Required |
| production_change | Required |

Provider and action allowlists are always required. Payloads are canonicalized as UTF-8 JSON with sorted keys and compact separators. NaN and Infinity are rejected. The default payload ceiling is 64 KiB; the hard configurable ceiling is 1 MiB. Attempts are bounded to 1–20 and lease TTL to 1–3600 seconds.

## Example

```python
from datetime import datetime, timezone

from integrations.federation.contracts import (
    ActionClass,
    ExecutionEnvelope,
    ExecutionPolicy,
    evaluate_policy,
)

policy = ExecutionPolicy(
    allowed_providers=frozenset({"cloudflare"}),
    allowed_actions=frozenset({"capture"}),
)

envelope = ExecutionEnvelope.build(
    execution_id="capture-001",
    provider="cloudflare",
    action="capture",
    action_class=ActionClass.READ_ONLY,
    idempotency_key="ixpansion:capture-001",
    payload={"url": "https://docs.example.test"},
    created_at=datetime.now(timezone.utc),
)

decision = evaluate_policy(envelope, policy)
assert decision.allowed
```

## Critical boundaries

- This package is a contract and policy evaluator, not an execution engine.
- It makes no network calls and does not acquire durable leases.
- It does not persist payloads, provider credentials, or raw result bodies.
- A SHA-256 digest proves byte-level correspondence only. It does not prove source authenticity, truth, freshness, or authorization.
- LIVE is a statement about the declared execution mode, not proof that a provider actually ran. Callers must only issue LIVE receipts after observing a real provider response.
- VERIFIED must be supplied only by a separate verifier with an explicit verification basis. The default receipt state is PENDING.
- Durable lease ownership, retries, cancellation, idempotent delivery, and outbox recovery remain the responsibility of the Workspace Nervous System.
- Provider adapters must not bypass this policy gate or reinterpret a denial as permission.

## Validation

Tests cover deterministic canonical hashing, malformed/non-finite payloads, payload bounds, timezone requirements, allowlist denials, approval gates, policy digest changes, and evidence receipt semantics. CI results for this branch are pending until GitHub Actions completes.
