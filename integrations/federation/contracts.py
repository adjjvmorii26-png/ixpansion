"""Shared policy and evidence contracts for federated provider execution.

This module is deliberately transport-free. It validates intent and records
content digests; it does not execute provider actions, acquire durable leases,
or claim that an external result is truthful.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.:-]{0,63}$")
_EXECUTION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_IDEMPOTENCY_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,191}$")


class ActionClass(str, Enum):
    READ_ONLY = "read_only"
    SANDBOX_WRITE = "sandbox_write"
    EXTERNAL_SIDE_EFFECT = "external_side_effect"
    PRODUCTION_CHANGE = "production_change"


class EvidenceMode(str, Enum):
    LIVE = "LIVE"
    SIMULATED = "SIMULATED"
    DEGRADED = "DEGRADED"


class VerificationState(str, Enum):
    VERIFIED = "VERIFIED"
    PENDING = "PENDING"
    CONTRADICTED = "CONTRADICTED"
    STALE = "STALE"


def _canonical_json(value: Any) -> bytes:
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError):
        raise ValueError("value must be finite, UTF-8 JSON data") from None
    return encoded


def _utc_timestamp(value: datetime) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _valid_names(values: frozenset[str], label: str) -> None:
    if not values:
        raise ValueError(f"{label} must not be empty")
    if any(not isinstance(value, str) or not _IDENTIFIER.fullmatch(value) for value in values):
        raise ValueError(f"{label} contains an invalid identifier")


@dataclass(frozen=True)
class ExecutionPolicy:
    """Allowlist and bounded execution limits shared by provider adapters."""

    allowed_providers: frozenset[str]
    allowed_actions: frozenset[str]
    max_payload_bytes: int = 65_536
    max_attempts: int = 3
    lease_ttl_seconds: int = 60
    require_approval_for: frozenset[ActionClass] = frozenset(
        {ActionClass.EXTERNAL_SIDE_EFFECT, ActionClass.PRODUCTION_CHANGE}
    )

    def __post_init__(self) -> None:
        _valid_names(self.allowed_providers, "allowed_providers")
        _valid_names(self.allowed_actions, "allowed_actions")
        for name, value, minimum, maximum in (
            ("max_payload_bytes", self.max_payload_bytes, 1, 1_048_576),
            ("max_attempts", self.max_attempts, 1, 20),
            ("lease_ttl_seconds", self.lease_ttl_seconds, 1, 3_600),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
                raise ValueError(f"{name} must be an integer between {minimum} and {maximum}")
        if not isinstance(self.require_approval_for, frozenset) or any(
            not isinstance(item, ActionClass) for item in self.require_approval_for
        ):
            raise ValueError("require_approval_for must be a frozenset of ActionClass values")

    def digest(self) -> str:
        """Return a stable digest of the complete policy configuration."""
        document = {
            "allowed_actions": sorted(self.allowed_actions),
            "allowed_providers": sorted(self.allowed_providers),
            "lease_ttl_seconds": self.lease_ttl_seconds,
            "max_attempts": self.max_attempts,
            "max_payload_bytes": self.max_payload_bytes,
            "require_approval_for": sorted(item.value for item in self.require_approval_for),
        }
        return hashlib.sha256(_canonical_json(document)).hexdigest()


@dataclass(frozen=True)
class ExecutionEnvelope:
    """Immutable, content-addressed description of one requested provider action."""

    execution_id: str
    provider: str
    action: str
    action_class: ActionClass
    idempotency_key: str
    payload_sha256: str
    payload_bytes: int
    created_at: str

    @classmethod
    def build(
        cls,
        *,
        execution_id: str,
        provider: str,
        action: str,
        action_class: ActionClass,
        idempotency_key: str,
        payload: Mapping[str, Any],
        created_at: datetime,
        max_payload_bytes: int = 65_536,
    ) -> "ExecutionEnvelope":
        if not isinstance(execution_id, str) or not _EXECUTION_ID.fullmatch(execution_id):
            raise ValueError("execution_id is invalid")
        if not isinstance(provider, str) or not _IDENTIFIER.fullmatch(provider):
            raise ValueError("provider is invalid")
        if not isinstance(action, str) or not _IDENTIFIER.fullmatch(action):
            raise ValueError("action is invalid")
        if not isinstance(action_class, ActionClass):
            raise ValueError("action_class must be an ActionClass")
        if not isinstance(idempotency_key, str) or not _IDEMPOTENCY_KEY.fullmatch(idempotency_key):
            raise ValueError("idempotency_key is invalid")
        if not isinstance(payload, Mapping):
            raise ValueError("payload must be a JSON object")
        if (
            isinstance(max_payload_bytes, bool)
            or not isinstance(max_payload_bytes, int)
            or not 1 <= max_payload_bytes <= 1_048_576
        ):
            raise ValueError("max_payload_bytes must be between 1 and 1048576")

        encoded = _canonical_json(payload)
        if len(encoded) > max_payload_bytes:
            raise ValueError("payload exceeds max_payload_bytes")
        return cls(
            execution_id=execution_id,
            provider=provider,
            action=action,
            action_class=action_class,
            idempotency_key=idempotency_key,
            payload_sha256=hashlib.sha256(encoded).hexdigest(),
            payload_bytes=len(encoded),
            created_at=_utc_timestamp(created_at),
        )


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str
    policy_sha256: str


def evaluate_policy(
    envelope: ExecutionEnvelope,
    policy: ExecutionPolicy,
    *,
    approved: bool = False,
) -> PolicyDecision:
    """Evaluate an envelope without invoking a provider or mutating state."""
    digest = policy.digest()
    if envelope.provider not in policy.allowed_providers:
        return PolicyDecision(False, "provider_not_allowed", digest)
    if envelope.action not in policy.allowed_actions:
        return PolicyDecision(False, "action_not_allowed", digest)
    if envelope.payload_bytes > policy.max_payload_bytes:
        return PolicyDecision(False, "payload_limit_exceeded", digest)
    if envelope.action_class in policy.require_approval_for and approved is not True:
        return PolicyDecision(False, "approval_required", digest)
    return PolicyDecision(True, "allowed", digest)


@dataclass(frozen=True)
class EvidenceReceipt:
    """Minimal evidence pointer; stores digests, not provider payloads or secrets."""

    execution_id: str
    provider: str
    action: str
    observed_at: str
    mode: EvidenceMode
    verification: VerificationState
    policy_sha256: str
    payload_sha256: str
    result_sha256: str

    @classmethod
    def from_result(
        cls,
        *,
        envelope: ExecutionEnvelope,
        policy: ExecutionPolicy,
        result: Mapping[str, Any],
        observed_at: datetime,
        mode: EvidenceMode,
        verification: VerificationState = VerificationState.PENDING,
    ) -> "EvidenceReceipt":
        if not isinstance(result, Mapping):
            raise ValueError("result must be a JSON object")
        if not isinstance(mode, EvidenceMode):
            raise ValueError("mode must be an EvidenceMode")
        if not isinstance(verification, VerificationState):
            raise ValueError("verification must be a VerificationState")
        result_bytes = _canonical_json(result)
        return cls(
            execution_id=envelope.execution_id,
            provider=envelope.provider,
            action=envelope.action,
            observed_at=_utc_timestamp(observed_at),
            mode=mode,
            verification=verification,
            policy_sha256=policy.digest(),
            payload_sha256=envelope.payload_sha256,
            result_sha256=hashlib.sha256(result_bytes).hexdigest(),
        )
