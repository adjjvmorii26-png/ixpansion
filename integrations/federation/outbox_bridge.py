"""Policy-gated handoff from federation contracts to the durable workspace outbox.

This bridge only enqueues authorized work. It never claims a lease or invokes a
provider; WorkspaceSyncRunner remains the only dispatch path.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from integrations.workspace_sync import WorkspaceOutbox

from .contracts import (
    ExecutionEnvelope,
    ExecutionPolicy,
    PolicyDecision,
    evaluate_policy,
)


@dataclass(frozen=True)
class EnqueueDecision:
    """Policy result plus whether a new durable outbox event was inserted."""

    policy: PolicyDecision
    enqueued: bool


def enqueue_if_authorized(
    outbox: WorkspaceOutbox,
    envelope: ExecutionEnvelope,
    policy: ExecutionPolicy,
    *,
    payload: dict,
    source: str,
    target: str,
    operation: str,
    approved: bool = False,
    idempotent: bool = True,
    now: float | None = None,
) -> EnqueueDecision:
    """Validate the payload binding, enforce policy, then enqueue exactly once.

    A denied action is never inserted. The supplied payload must be byte-for-byte
    equivalent under the shared canonical JSON rules to the envelope digest.
    """
    if not isinstance(outbox, WorkspaceOutbox):
        raise TypeError("outbox must be a WorkspaceOutbox")
    if not isinstance(envelope, ExecutionEnvelope):
        raise TypeError("envelope must be an ExecutionEnvelope")
    if not isinstance(policy, ExecutionPolicy):
        raise TypeError("policy must be an ExecutionPolicy")
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    if target != envelope.provider:
        raise ValueError("outbox target must match the policy-authorized provider")

    try:
        created_at = datetime.fromisoformat(envelope.created_at.replace("Z", "+00:00"))
        rebuilt = ExecutionEnvelope.build(
            execution_id=envelope.execution_id,
            provider=envelope.provider,
            action=envelope.action,
            action_class=envelope.action_class,
            idempotency_key=envelope.idempotency_key,
            payload=payload,
            created_at=created_at,
            max_payload_bytes=policy.max_payload_bytes,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"payload does not satisfy the execution envelope: {exc}") from None

    if (
        rebuilt.payload_sha256 != envelope.payload_sha256
        or rebuilt.payload_bytes != envelope.payload_bytes
        or rebuilt.created_at != envelope.created_at
    ):
        raise ValueError("payload does not match the execution envelope digest")

    decision = evaluate_policy(envelope, policy, approved=approved)
    if not decision.allowed:
        return EnqueueDecision(policy=decision, enqueued=False)

    inserted = outbox.enqueue(
        idempotency_key=envelope.idempotency_key,
        source=source,
        target=target,
        operation=operation,
        payload=payload,
        idempotent=idempotent,
        now=now,
    )
    return EnqueueDecision(policy=decision, enqueued=inserted)
