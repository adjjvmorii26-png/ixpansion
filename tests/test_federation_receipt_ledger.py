from datetime import datetime, timezone
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from integrations.federation.contracts import (
    ActionClass,
    EvidenceMode,
    EvidenceReceipt,
    ExecutionEnvelope,
    ExecutionPolicy,
)
from integrations.federation.receipt_ledger import ReceiptLedger


NOW = datetime(2026, 11, 17, 12, 0, tzinfo=timezone.utc)


class ReceiptLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "ledger.sqlite3"
        self.ledger = ReceiptLedger(self.path)
        self.policy = ExecutionPolicy(
            allowed_providers=frozenset({"notion"}),
            allowed_actions=frozenset({"upsert"}),
        )
        self.envelope = ExecutionEnvelope.build(
            execution_id="exec-ledger-001",
            provider="notion",
            action="upsert",
            action_class=ActionClass.READ_ONLY,
            idempotency_key="ixpansion:exec-ledger-001",
            payload={"artifact": "pr-425"},
            created_at=NOW,
        )

    def tearDown(self):
        self.temp.cleanup()

    def make_receipt(self):
        return EvidenceReceipt.from_result(
            envelope=self.envelope,
            policy=self.policy,
            result={"read_back": True},
            observed_at=NOW,
            mode=EvidenceMode.LIVE,
        )

    def test_lifecycle_events_form_a_valid_chain(self):
        first = self.ledger.append(
            execution_id="exec-ledger-001",
            event_kind="enqueued",
            occurred_at=NOW,
            details={"outbox_event_id": 7},
        )
        second = self.ledger.append(
            execution_id="exec-ledger-001",
            event_kind="claimed",
            occurred_at=NOW,
            details={"attempt": 1},
        )
        receipt = self.ledger.append(
            execution_id="exec-ledger-001",
            event_kind="receipt_recorded",
            occurred_at=NOW,
            receipt=self.make_receipt(),
        )

        self.assertEqual(first["sequence"], 1)
        self.assertEqual(second["previous_hash"], first["event_hash"])
        self.assertEqual(receipt["sequence"], 3)
        self.assertTrue(self.ledger.verify_chain()["valid"])
        self.assertEqual(len(self.ledger.read(execution_id="exec-ledger-001")), 3)

    def test_receipt_cannot_be_attached_to_another_execution(self):
        with self.assertRaises(ValueError, msg="receipt execution_id"):
            self.ledger.append(
                execution_id="exec-other",
                event_kind="receipt_recorded",
                occurred_at=NOW,
                receipt=self.make_receipt(),
            )

    def test_receipt_is_required_only_for_receipt_event(self):
        with self.assertRaises(ValueError):
            self.ledger.append(
                execution_id="exec-ledger-001",
                event_kind="receipt_recorded",
                occurred_at=NOW,
            )
        with self.assertRaises(ValueError):
            self.ledger.append(
                execution_id="exec-ledger-001",
                event_kind="claimed",
                occurred_at=NOW,
                receipt=self.make_receipt(),
            )

    def test_secret_like_details_are_rejected(self):
        with self.assertRaises(ValueError):
            self.ledger.append(
                execution_id="exec-ledger-001",
                event_kind="dispatched",
                occurred_at=NOW,
                details={"access_token": "never-store"},
            )
        self.assertEqual(self.ledger.verify_chain()["checked"], 0)

    def test_non_scalar_and_unbounded_details_are_rejected(self):
        with self.assertRaises(ValueError):
            self.ledger.append(
                execution_id="exec-ledger-001",
                event_kind="dispatched",
                occurred_at=NOW,
                details={"nested": {"raw": "payload"}},
            )
        with self.assertRaises(ValueError):
            self.ledger.append(
                execution_id="exec-ledger-001",
                event_kind="dispatched",
                occurred_at=NOW,
                details={"label": "x" * 201},
            )

    def test_ledger_rows_reject_update_and_delete(self):
        self.ledger.append(
            execution_id="exec-ledger-001",
            event_kind="enqueued",
            occurred_at=NOW,
        )
        with sqlite3.connect(self.path) as db:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("DELETE FROM federation_receipt_ledger WHERE sequence=1")
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("UPDATE federation_receipt_ledger SET event_hash='bad' WHERE sequence=1")

    def test_hash_chain_detects_database_tampering(self):
        self.ledger.append(
            execution_id="exec-ledger-001",
            event_kind="enqueued",
            occurred_at=NOW,
            details={"attempt": 1},
        )
        with sqlite3.connect(self.path) as db:
            db.execute("DROP TRIGGER federation_ledger_no_update")
            db.execute(
                "UPDATE federation_receipt_ledger SET event_json=? WHERE sequence=1",
                ('{"details":{"attempt":2},"event_kind":"enqueued","execution_id":"exec-ledger-001","occurred_at":"2026-11-17T12:00:00.000000Z","receipt":null}',),
            )
        result = self.ledger.verify_chain()
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "event_hash_mismatch")

    def test_parallel_appends_preserve_a_single_chain(self):
        barrier = threading.Barrier(5)
        failures = []

        def worker(index):
            try:
                barrier.wait()
                ReceiptLedger(self.path).append(
                    execution_id=f"exec-ledger-{index}",
                    event_kind="enqueued",
                    occurred_at=NOW,
                    details={"worker": index},
                )
            except Exception as exc:
                failures.append(exc)

        threads = [threading.Thread(target=worker, args=(index,)) for index in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(failures, [])
        result = self.ledger.verify_chain()
        self.assertTrue(result["valid"])
        self.assertEqual(result["checked"], 5)


if __name__ == "__main__":
    unittest.main()
