from datetime import datetime, timezone

import pytest

from integrations.federation.contracts import (
    ActionClass,
    EvidenceMode,
    EvidenceReceipt,
    ExecutionEnvelope,
    ExecutionPolicy,
    VerificationState,
    evaluate_policy,
)


NOW = datetime(2026, 11, 15, 12, 0, tzinfo=timezone.utc)


def make_policy(**overrides):
    values = {
        "allowed_providers": frozenset({"cloudflare", "notion"}),
        "allowed_actions": frozenset({"capture", "upsert"}),
    }
    values.update(overrides)
    return ExecutionPolicy(**values)


def make_envelope(
    *,
    provider="cloudflare",
    action="capture",
    action_class=ActionClass.READ_ONLY,
    payload=None,
):
    return ExecutionEnvelope.build(
        execution_id="exec-001",
        provider=provider,
        action=action,
        action_class=action_class,
        idempotency_key="ixpansion:exec-001",
        payload={"target": "https://docs.example.test"} if payload is None else payload,
        created_at=NOW,
    )


def test_envelope_hash_is_stable_for_equivalent_json_objects():
    left = make_envelope(payload={"b": 2, "a": 1})
    right = make_envelope(payload={"a": 1, "b": 2})

    assert left.payload_sha256 == right.payload_sha256
    assert left.payload_bytes == right.payload_bytes


def test_envelope_rejects_oversized_payload():
    with pytest.raises(ValueError, match="exceeds"):
        make_envelope(payload={"blob": "x" * 128},)


def test_envelope_rejects_non_finite_json_values():
    with pytest.raises(ValueError, match="finite"):
        make_envelope(payload={"score": float("nan")})


def test_envelope_requires_timezone_aware_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        ExecutionEnvelope.build(
            execution_id="exec-001",
            provider="cloudflare",
            action="capture",
            action_class=ActionClass.READ_ONLY,
            idempotency_key="ixpansion:exec-001",
            payload={},
            created_at=datetime(2026, 11, 15, 12, 0),
        )


def test_policy_rejects_provider_and_action_not_on_allowlist():
    policy = make_policy()

    assert evaluate_policy(make_envelope(provider="github"), policy).reason == "provider_not_allowed"
    assert evaluate_policy(make_envelope(action="delete"), policy).reason == "action_not_allowed"


def test_external_side_effect_requires_explicit_approval():
    policy = make_policy(allowed_actions=frozenset({"publish"}))
    envelope = make_envelope(action="publish", action_class=ActionClass.EXTERNAL_SIDE_EFFECT)

    denied = evaluate_policy(envelope, policy)
    allowed = evaluate_policy(envelope, policy, approved=True)

    assert (denied.allowed, denied.reason) == (False, "approval_required")
    assert (allowed.allowed, allowed.reason) == (True, "allowed")


def test_production_change_is_approval_gated_by_default():
    policy = make_policy(allowed_actions=frozenset({"deploy"}))
    envelope = make_envelope(action="deploy", action_class=ActionClass.PRODUCTION_CHANGE)

    assert evaluate_policy(envelope, policy).reason == "approval_required"


def test_policy_digest_changes_when_limits_change():
    first = make_policy(max_attempts=2)
    second = make_policy(max_attempts=3)

    assert first.digest() != second.digest()
    assert first.digest() == make_policy(max_attempts=2).digest()


def test_evidence_receipt_binds_policy_payload_and_result_without_storing_payload():
    policy = make_policy()
    envelope = make_envelope()
    receipt = EvidenceReceipt.from_result(
        envelope=envelope,
        policy=policy,
        result={"status": "captured", "count": 3},
        observed_at=NOW,
        mode=EvidenceMode.LIVE,
    )

    assert receipt.execution_id == envelope.execution_id
    assert receipt.policy_sha256 == policy.digest()
    assert receipt.payload_sha256 == envelope.payload_sha256
    assert len(receipt.result_sha256) == 64
    assert receipt.mode is EvidenceMode.LIVE
    assert receipt.verification is VerificationState.PENDING
    assert not hasattr(receipt, "result")


def test_simulated_receipt_does_not_claim_verified_truth():
    receipt = EvidenceReceipt.from_result(
        envelope=make_envelope(),
        policy=make_policy(),
        result={"status": "simulated"},
        observed_at=NOW,
        mode=EvidenceMode.SIMULATED,
    )

    assert receipt.mode is EvidenceMode.SIMULATED
    assert receipt.verification is VerificationState.PENDING


def test_receipt_rejects_naive_observation_time():
    with pytest.raises(ValueError, match="timezone-aware"):
        EvidenceReceipt.from_result(
            envelope=make_envelope(),
            policy=make_policy(),
            result={},
            observed_at=datetime(2026, 11, 15, 12, 0),
            mode=EvidenceMode.LIVE,
        )
