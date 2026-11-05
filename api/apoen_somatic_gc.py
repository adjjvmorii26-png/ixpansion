"""APOEN-0: policy-only somatic timeline garbage collection.

This module never deletes remote state. It verifies signed heartbeats, scores
staleness from explicit telemetry, protects live lineage/leases, and emits
hash-chained recommendation receipts for a later approval-gated executor.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any, Mapping


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sign_heartbeat(payload: Mapping[str, Any], secret: bytes) -> str:
    """Create a SHA-256 HMAC over the canonical heartbeat payload."""
    if not isinstance(secret, bytes) or not secret:
        raise ValueError("heartbeat secret must be non-empty bytes")
    return hmac.new(secret, canonical_json(dict(payload)).encode("utf-8"), hashlib.sha256).hexdigest()


def verify_heartbeat(payload: Mapping[str, Any], signature: str, secret: bytes) -> bool:
    if not isinstance(secret, bytes) or not secret or not isinstance(signature, str):
        return False
    try:
        expected = sign_heartbeat(payload, secret)
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(expected, signature)


@dataclass(frozen=True)
class GCPolicy:
    stale_after_seconds: int = 3600
    minimum_age_seconds: int = 86400
    maximum_interactions: int = 0

    def __post_init__(self) -> None:
        values = (self.stale_after_seconds, self.minimum_age_seconds, self.maximum_interactions)
        if any(type(value) is not int for value in values):
            raise ValueError("policy thresholds must be integers")
        if self.stale_after_seconds < 1 or self.minimum_age_seconds < 1:
            raise ValueError("age thresholds must be positive")
        if self.maximum_interactions < 0:
            raise ValueError("maximum_interactions cannot be negative")


class SomaticGarbageCollector:
    """Deterministic, non-destructive candidate evaluator."""

    def __init__(self, cluster_id: str, policy: GCPolicy | None = None) -> None:
        if not isinstance(cluster_id, str) or not cluster_id.strip():
            raise ValueError("cluster_id must be non-empty")
        self.cluster_id = cluster_id
        self.policy = policy or GCPolicy()

    @staticmethod
    def _retained(branch_id: str, cluster_id: str, reason: str, **details: Any) -> dict[str, Any]:
        return {
            "branch_id": branch_id,
            "cluster_id": cluster_id,
            "decision": "RETAIN",
            "eligible": False,
            "reason": reason,
            "destructive_action_performed": False,
            **details,
        }

    def evaluate_authenticated_branch(
        self,
        branch_id: str,
        metadata: Mapping[str, Any],
        heartbeat_payload: Mapping[str, Any],
        signature: str,
        secret: bytes,
        *,
        now: int,
    ) -> dict[str, Any]:
        """Evaluate only when the signed heartbeat is bound to this branch and cluster."""
        if not isinstance(heartbeat_payload, Mapping) or not isinstance(metadata, Mapping):
            return self._retained(branch_id, self.cluster_id, "invalid_heartbeat")
        # Bind every decision-bearing field, not just liveness identity.
        # Otherwise an attacker could keep a valid heartbeat but alter age or
        # interaction_count to make an active branch appear collectible.
        bound_fields = ("created_at", "last_heartbeat", "interaction_count",
                        "protected", "has_live_descendants", "active_lease")
        expected = {"branch_id": branch_id, "cluster_id": self.cluster_id}
        expected.update({key: metadata[key] for key in bound_fields if key in metadata})
        if any(heartbeat_payload.get(key) != value for key, value in expected.items()):
            return self._retained(branch_id, self.cluster_id, "heartbeat_binding_mismatch")
        if not verify_heartbeat(heartbeat_payload, signature, secret):
            return self._retained(branch_id, self.cluster_id, "invalid_heartbeat")
        return self.evaluate_branch(branch_id, metadata, now=now)

    def evaluate_branch(self, branch_id: str, metadata: Mapping[str, Any], *, now: int) -> dict[str, Any]:
        if not isinstance(branch_id, str) or not branch_id.strip():
            raise ValueError("branch_id must be non-empty")
        if not isinstance(metadata, Mapping) or type(now) is not int or now < 0:
            return self._retained(branch_id, self.cluster_id, "invalid_telemetry")

        required = ("created_at", "last_heartbeat", "interaction_count")
        missing = [key for key in required if key not in metadata]
        if missing:
            return self._retained(branch_id, self.cluster_id, "missing_telemetry", missing_fields=missing)

        values = (metadata["created_at"], metadata["last_heartbeat"], metadata["interaction_count"])
        if any(type(value) is not int or value < 0 for value in values):
            return self._retained(branch_id, self.cluster_id, "invalid_telemetry")
        created_at, heartbeat, interactions = values
        if created_at > now or heartbeat > now:
            return self._retained(branch_id, self.cluster_id, "future_timestamp")

        guards = ("protected", "has_live_descendants", "active_lease")
        malformed_guards = [key for key in guards if key in metadata and type(metadata[key]) is not bool]
        if malformed_guards:
            return self._retained(branch_id, self.cluster_id, "invalid_topology_guard", invalid_fields=malformed_guards)
        active_guards = [key for key in guards if metadata.get(key) is True]
        if active_guards:
            return self._retained(branch_id, self.cluster_id, "lineage_or_lease_protected", active_guards=active_guards)

        age = now - created_at
        heartbeat_age = now - heartbeat
        checks = {
            "old_enough": age >= self.policy.minimum_age_seconds,
            "heartbeat_stale": heartbeat_age >= self.policy.stale_after_seconds,
            "low_activity": interactions <= self.policy.maximum_interactions,
            "lineage_unprotected": True,
            "lease_inactive": True,
        }
        eligible = all(checks.values())
        return {
            "branch_id": branch_id,
            "cluster_id": self.cluster_id,
            "decision": "CANDIDATE" if eligible else "RETAIN",
            "eligible": eligible,
            "reason": "all_policy_checks_passed" if eligible else "policy_checks_not_satisfied",
            "age_seconds": age,
            "heartbeat_age_seconds": heartbeat_age,
            "interaction_count": interactions,
            "checks": checks,
            "destructive_action_performed": False,
        }

    @staticmethod
    def seal_receipt(evaluation: Mapping[str, Any], *, previous_seal: str = "") -> dict[str, Any]:
        """Create a deterministic receipt; callers must persist it append-only."""
        body = {
            "schema": "apoen.receipt.v1",
            "previous_seal": previous_seal,
            "evaluation": dict(evaluation),
            "action": "recommendation_only",
        }
        seal = hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()
        return {**body, "seal": seal}


def verify_receipt(receipt: Mapping[str, Any]) -> bool:
    try:
        body = {
            "schema": receipt["schema"],
            "previous_seal": receipt["previous_seal"],
            "evaluation": receipt["evaluation"],
            "action": receipt["action"],
        }
        expected = hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()
        return hmac.compare_digest(expected, str(receipt["seal"]))
    except (KeyError, TypeError, ValueError):
        return False


def handler(payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    action = payload.get("action", "status")
    if action == "status":
        return {
            "module": "apoen_somatic_gc",
            "version": "0.1",
            "status": "experimental",
            "mode": "policy_only",
            "destructive_actions_enabled": False,
        }
    return {"error": "unsupported action", "available": ["status"]}
