from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from integrations.workspace_sync import (
    PermanentAdapterError,
    TransientAdapterError,
    WorkspaceOutbox,
    WorkspaceSyncRunner,
)


class ShadowProvider:
    """Deterministic fake provider with controllable faults and read-back."""

    def __init__(self, *, fail_first=False, deny=False, mismatch=False):
        self.remote = {}
        self.write_attempts = 0
        self.fail_first = fail_first
        self.deny = deny
        self.mismatch = mismatch

    def deliver(self, event):
        self.write_attempts += 1
        if self.deny:
            raise PermanentAdapterError("provider denied write: insufficient scope")
        if self.fail_first:
            self.fail_first = False
            raise TransientAdapterError("simulated provider timeout")
        self.remote[event["idempotency_key"]] = dict(event["payload"])
        return {
            "idempotency_key": event["idempotency_key"],
            "payload_hash": event["payload_hash"],
        }

    def verify(self, event, receipt):
        if self.mismatch:
            return False
        return (
            receipt.get("idempotency_key") == event["idempotency_key"]
            and receipt.get("payload_hash") == event["payload_hash"]
            and self.remote.get(event["idempotency_key"]) == event["payload"]
        )


class WorkspaceShadowTwinTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.queue = WorkspaceOutbox(
            Path(self.temp.name) / "shadow.sqlite3",
            retry_base_seconds=5,
            retry_max_seconds=30,
        )

    def tearDown(self):
        self.temp.cleanup()

    def enqueue(self, *, target, revision="sha-1", now=100):
        key = f"github:commit:{revision}:{target}:upsert"
        return self.queue.enqueue(
            idempotency_key=key,
            source="github",
            target=target,
            operation="upsert_artifact",
            payload={"artifact_id": "report-7", "source_revision": revision, "sha256": f"hash-{revision}"},
            idempotent=True,
            now=now,
        )

    def test_partial_fanout_retries_only_the_failed_destination(self):
        self.enqueue(target="notion")
        self.enqueue(target="drive")
        notion = ShadowProvider()
        drive = ShadowProvider(fail_first=True)
        runner = WorkspaceSyncRunner(self.queue, {"notion": notion, "drive": drive})

        first = runner.run_once(now=100)
        self.assertCountEqual([item["state"] for item in first], ["delivered_verified", "pending"])
        self.assertEqual(notion.write_attempts, 1)
        self.assertEqual(drive.write_attempts, 1)
        self.assertEqual(self.queue.stats()["delivered"], 1)
        self.assertEqual(self.queue.stats()["pending"], 1)

        second = runner.run_once(now=105)
        self.assertEqual(second[0]["state"], "delivered_verified")
        self.assertEqual(notion.write_attempts, 1, "successful Notion leg must not replay")
        self.assertEqual(drive.write_attempts, 2)
        self.assertEqual(self.queue.stats()["delivered"], 2)
        self.assertEqual(self.queue.stats()["pending"], 0)

    def test_duplicate_event_replay_creates_one_remote_artifact(self):
        self.assertTrue(self.enqueue(target="drive"))
        self.assertFalse(self.enqueue(target="drive"))
        provider = ShadowProvider()
        runner = WorkspaceSyncRunner(self.queue, {"drive": provider})
        runner.run_once(now=100)
        runner.run_once(now=200)
        self.assertEqual(provider.write_attempts, 1)
        self.assertEqual(len(provider.remote), 1)

    def test_permission_denial_is_quarantined_not_retried(self):
        self.enqueue(target="notion")
        provider = ShadowProvider(deny=True)
        runner = WorkspaceSyncRunner(self.queue, {"notion": provider})
        result = runner.run_once(now=100)
        self.assertEqual(result[0]["state"], "dead")
        self.assertEqual(self.queue.stats()["dead"], 1)
        self.assertEqual(self.queue.claim_due(now=1000), [])
        self.assertEqual(provider.write_attempts, 1)

    def test_readback_mismatch_is_not_marked_delivered(self):
        self.enqueue(target="drive")
        provider = ShadowProvider(mismatch=True)
        runner = WorkspaceSyncRunner(self.queue, {"drive": provider})
        result = runner.run_once(now=100)
        self.assertEqual(result[0]["state"], "dead")
        self.assertEqual(self.queue.stats()["delivered"], 0)
        self.assertEqual(self.queue.stats()["dead"], 1)

    def test_source_revision_change_creates_a_distinct_immutable_event(self):
        self.assertTrue(self.enqueue(target="drive", revision="sha-1"))
        self.assertTrue(self.enqueue(target="drive", revision="sha-2"))
        provider = ShadowProvider()
        runner = WorkspaceSyncRunner(self.queue, {"drive": provider})
        result = runner.run_once(now=100)
        self.assertEqual(len(result), 2)
        self.assertEqual(self.queue.stats()["delivered"], 2)
        self.assertEqual(len(provider.remote), 2)
        revisions = {item["source_revision"] for item in provider.remote.values()}
        self.assertEqual(revisions, {"sha-1", "sha-2"})


if __name__ == "__main__":
    unittest.main()
