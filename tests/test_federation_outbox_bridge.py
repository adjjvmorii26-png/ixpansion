from datetime import datetime, timezone
import tempfile
from pathlib import Path

import pytest

from integrations.federation.contracts import (
    ActionClass,
    ExecutionEnvelope,
    ExecutionPolicy,
)
from integrations.federation.outbox_bridge import enqueue_if_authorized
from integrations.workspace_sync import WorkspaceOutbox


NOW = datetime(2026, 11, 17, 12, 0, tzinfo=timezone.utc)
PAYLOAD = {"target": "https://docs.example.test", "label": "café"}


@pytest.fixture
def outbox():
    with tempfile.TemporaryDirectory() as directory:
        yield WorkspaceOutbox(Path(directory) / "outbox.sqlite3")


def policy(**overrides):
    values = {
        "allowed_providers": frozenset({"cloudflare"}),
        "allowed_actions": frozenset({"capture", "publish"}),
    }
    values.update(overrides)
    return ExecutionPolicy(**values)


def envelope(payload=PAYLOAD, *, action="capture", action_class=ActionClass.READ_ONLY):
    return ExecutionEnvelope.build(
        execution_id="exec-bridge-001",
        provider="cloudflare",
        action=action,
        action_class=action_class,
        idempotency_key="ixpansion:exec-bridge-001",
        payload=payload,
        created_at=NOW,
    )


def enqueue(outbox, item, selected_policy, **kwargs):
    return enqueue_if_authorized(
        outbox,
        item,
        selected_policy,
        payload=kwargs.pop("payload", PAYLOAD),
        source="github",
        target="notion",
        operation="upsert_artifact_pointer",
        now=100,
        **kwargs,
    )


def test_authorized_action_is_enqueued_once(outbox):
    item = envelope()
    selected_policy = policy()

    first = enqueue(outbox, item, selected_policy)
    replay = enqueue(outbox, item, selected_policy)

    assert first.policy.allowed is True
    assert first.enqueued is True
    assert replay.enqueued is False
    assert outbox.stats()["pending"] == 1


def test_policy_denial_does_not_insert_event(outbox):
    result = enqueue(outbox, envelope(), policy(allowed_actions=frozenset({"publish"})))

    assert result.policy.reason == "action_not_allowed"
    assert result.enqueued is False
    assert outbox.stats()["pending"] == 0


def test_external_side_effect_is_not_enqueued_without_approval(outbox):
    item = envelope(action="publish", action_class=ActionClass.EXTERNAL_SIDE_EFFECT)

    denied = enqueue(outbox, item, policy())
    approved = enqueue(outbox, item, policy(), approved=True)

    assert denied.policy.reason == "approval_required"
    assert denied.enqueued is False
    assert approved.enqueued is True
    assert outbox.stats()["pending"] == 1


def test_payload_digest_mismatch_is_rejected_before_enqueue(outbox):
    with pytest.raises(ValueError, match="does not match"):
        enqueue(outbox, envelope(), policy(), payload={"target": "https://evil.example.test"})

    assert outbox.stats()["pending"] == 0


def test_unicode_payload_hash_matches_workspace_outbox_canonicalization(outbox):
    item = envelope(payload=PAYLOAD)
    result = enqueue(outbox, item, policy())

    assert result.enqueued is True
    stored = outbox.get(1)
    assert stored["payload"] == PAYLOAD
    assert stored["payload_hash"] == item.payload_sha256


def test_outbox_rejects_secret_payload_even_after_policy_allows(outbox):
    secret_payload = {"access_token": "not-stored"}
    item = envelope(payload=secret_payload)

    with pytest.raises(Exception, match="credential-like"):
        enqueue(outbox, item, policy(), payload=secret_payload)

    assert outbox.stats()["pending"] == 0
