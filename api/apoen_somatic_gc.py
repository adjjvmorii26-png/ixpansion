"""APOEN-0: policy-only somatic timeline garbage collection.

This module never deletes remote state. It verifies signed heartbeats, scores
staleness from explicit telemetry, and emits hash-chained recommendation
receipts suitable for a later approval-gated executor.
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
    if not secret:
        raise ValueError("heartbeat secret must not be empty")
    return hmac.new(secret, canonical_json(dict(payload)).encode("utf-8"), hashlib.sha256).hexdigest()


def verify_heartbeat(payload: Mapping[str, Any], signature: str, secret: bytes) -> bool:
    if not secret or not isinstance(signature, str):
        return False
    expected = sign_heartbeat(payload, secret)
    return hmac.compare_digest(expected, signature)


@dataclass(frozen=True)
class GCPolicy:
    stale_after_seconds: int = 3600
    minimum_age_seconds: int = 86400
    maximum_interactions: int = 0

    def __post_init__(self) -> None:
        if self.stale_after_seconds < 1 or self.minimum_age_seconds < 1:
            raise ValueError("age thresholds must be positive")
        if self.maximum_interactions < 0:
            raise ValueError("maximum_interactions cannot be negative")


class SomaticGarbageCollector:
    """Deterministic, non-destructive candidate evaluator."""

    def __init__(self, cluster_id: str, policy: GCPolicy | None = None) -> None:
        if not cluster_id or not cluster_id.strip():
            raise ValueError("cluster_id must be non-empty")
        self.cluster_id = cluster_id
        self.policy = policy or GCPolicy()

    def evaluate_branch(self, branch_id: str, metadata: Mapping[str, Any], *, now: int) -> dict[str, Any]:
        if not branch_id or not branch_id.strip():
            raise ValueError("branch_id must be non-empty")
        required = ("created_at", "last_heartbeat", "interaction_count")
        missing = [key for key in required if key not in metadata]
        if missing:
            return {
                "branch_id": branch_id,
                "decision": "RETAIN",
                "eligible": False,
                "reason": "missing_telemetry",
                "missing_fields": missing,
                "cluster_id": self.cluster_id,
            }
        try:
            created_at = int(metadata["created_at"])
            heartbeat = int(metadata["last_heartbeat"])
            interactions = int(metadata["interaction_count"])
        except (TypeError, ValueError, OverflowError):
            return {
                "branch_id": branch_id,
                "decision": "RETAIN",
                "eligible": False,
                "reason": "invalid_telemetry",
                "cluster_id": self.cluster_id,
            }
        if min(created_at, heartbeat, interactions, now) < 0 or interactions < 0:
            return {
                "branch_id": branch_id,
                "decision": "RETAIN",
                "eligible": False,
                "reason": "invalid_telemetry",
                "cluster_id": self.cluster_id,
            }
        age = max(0, now - created_at)
        heartbeat_age = max(0, now - heartbeat)
        checks = {
            "old_enough": age >= self.policy.minimum_age_seconds,
            "heartbeat_stale": heartbeat_age >= self.policy.stale_after_seconds,
            "low_activity": interactions <= self.policy.maximum_interactions,
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
