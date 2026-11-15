from __future__ import annotations

import tempfile
import threading
import unittest
from pathlib import Path

from integrations.workspace_sync import (
    IdempotencyConflict,
    InvalidEvent,
    PermanentAdapterError,
    TransientAdapterError,
    WorkspaceOutbox,
    WorkspaceSyncRunner,
)


class FakeAdapter:
    def __init__(self, *, verify=True, failure=None):
        self.verify_result = verify
        self.failure = failure
        self.delivered = []

    def deliver(self, event):
        if self.failure:
            raise self.failure
        self.delivered.append(event["idempotency_key"])
        return {"destination_id": "artifact-1", "verified": self.verify_result}

    def verify(self, event, receipt):
        return self.verify_result and receipt.get("verified") is True


class WorkspaceOutboxTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "outbox.sqlite3"
        self.queue = WorkspaceOutbox(self.db, retry_base_seconds=5, retry_max_seconds=20)

    def tearDown(self):
        self.temp.cleanup()

    def enqueue(self, key="evt-1", *, idempotent=True, payload=None, now=100):
        return self.queue.enqueue(
            idempotency_key=key,
            source="github",
            target="notion",
            operation="upsert_artifact_pointer",
            payload=payload or {"artifact_id": "a-1", "sha256": "abc"},
            idempotent=idempotent,
            now=now,
        )

    def test_exact_replay_is_noop(self):
        self.assertTrue(self.enqueue())
        self.assertFalse(self.enqueue())
        self.assertEqual(self.queue.stats()["pending"], 1)

    def test_key_collision_with_changed_payload_is_rejected(self):
        self.enqueue()
        with self.assertRaises(IdempotencyConflict):
            self.enqueue(payload={"artifact_id": "different"})

    def test_credential_like_fields_are_rejected_recursively(self):
        with self.assertRaises(InvalidEvent):
            self.enqueue(payload={"metadata": {"access_token": "never-store-this"}})

    def test_claim_is_exclusive_under_concurrent_workers(self):
        self.enqueue()
        barrier = threading.Barrier(3)
        claimed = []

        def worker():
            barrier.wait()
            claimed.extend(self.queue.claim_due(now=100, limit=1))

        threads = [threading.Thread(target=worker) for _ in range(2)]
        for thread in threads:
            thread.start()
        barrier.wait()
        for thread in threads:
            thread.join()
        self.assertEqual(len(claimed), 1)

    def test_expired_idempotent_lease_is_requeued(self):
        self.enqueue()
        first = self.queue.claim_due(now=100, lease_seconds=2)[0]
        self.assertEqual(first["attempts"], 1)
        second = self.queue.claim_due(now=103, lease_seconds=2)[0]
        self.assertEqual(second["event_id"], first["event_id"])
        self.assertEqual(second["attempts"], 2)

    def test_expired_non_idempotent_lease_is_dead_lettered(self):
        self.enqueue(idempotent=False)
        first = self.queue.claim_due(now=100, lease_seconds=2)[0]
        self.assertEqual(first["state"], "inflight")
        self.assertEqual(self.queue.claim_due(now=103), [])
        self.assertEqual(self.queue.get(first["event_id"])["state"], "dead")

    def test_transient_failure_retries_only_idempotent_events(self):
        self.enqueue()
        event = self.queue.claim_due(now=100)[0]
        self.assertEqual(self.queue.mark_failed(event["event_id"], "timeout", transient=True, now=100), "pending")
        self.assertEqual(self.queue.claim_due(now=104), [])
        self.assertEqual(len(self.queue.claim_due(now=105)), 1)

    def test_non_idempotent_transient_failure_is_not_retried(self):
        self.enqueue(idempotent=False)
        event = self.queue.claim_due(now=100)[0]
        self.assertEqual(self.queue.mark_failed(event["event_id"], "timeout", transient=True, now=100), "dead")

    def test_error_text_is_redacted(self):
        self.enqueue()
        event = self.queue.claim_due(now=100)[0]
        self.queue.mark_failed(event["event_id"], "Bearer abc.def and access_token=supersecret", transient=False, now=100)
        error = self.queue.get(event["event_id"])["last_error"]
        self.assertNotIn("abc.def", error)
        self.assertNotIn("supersecret", error)

    def test_runner_requires_read_after_write_verification(self):
        self.enqueue()
        adapter = FakeAdapter(verify=True)
        runner = WorkspaceSyncRunner(self.queue, {"notion": adapter})
        result = runner.run_once(now=100)
        self.assertEqual(result[0]["state"], "delivered_verified")
        self.assertEqual(self.queue.stats()["delivered"], 1)

    def test_runner_dead_letters_unverified_write(self):
        self.enqueue()
        adapter = FakeAdapter(verify=False)
        runner = WorkspaceSyncRunner(self.queue, {"notion": adapter})
        result = runner.run_once(now=100)
        self.assertEqual(result[0]["state"], "dead")
        self.assertEqual(self.queue.stats()["dead"], 1)

    def test_runner_retries_transient_adapter_error(self):
        self.enqueue()
        adapter = FakeAdapter(failure=TransientAdapterError("provider timeout"))
        runner = WorkspaceSyncRunner(self.queue, {"notion": adapter})
        result = runner.run_once(now=100)
        self.assertEqual(result[0]["state"], "pending")

    def test_runner_does_not_retry_unclassified_errors(self):
        self.enqueue()
        adapter = FakeAdapter(failure=RuntimeError("unexpected"))
        runner = WorkspaceSyncRunner(self.queue, {"notion": adapter})
        result = runner.run_once(now=100)
        self.assertEqual(result[0]["state"], "dead")

    def test_dry_run_does_not_claim_or_mutate(self):
        self.enqueue()
        runner = WorkspaceSyncRunner(self.queue, {})
        result = runner.run_once(now=100, dry_run=True)
        self.assertEqual(result[0]["state"], "would_dispatch")
        self.assertEqual(self.queue.stats()["pending"], 1)
        self.assertEqual(self.queue.stats()["inflight"], 0)


if __name__ == "__main__":
    unittest.main()
