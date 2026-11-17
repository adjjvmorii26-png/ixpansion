"""Append-only, hash-chained execution history for federation evidence.

The ledger stores lifecycle facts and compact receipt digests, never provider
payloads, credentials, or raw result bodies. It is an audit aid, not a source
of truth: a valid hash chain proves internal continuity, not event authenticity.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .contracts import EvidenceReceipt


_GENESIS = "0" * 64
_SECRET_KEY = re.compile(r"(secret|token|password|authorization|api[_-]?key|private[_-]?key)", re.I)
_EXECUTION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_EVENT_KINDS = frozenset({
    "enqueued", "claimed", "dispatched", "retry_scheduled", "lease_expired",
    "delivery_verified", "delivery_unverified", "dead_lettered",
    "receipt_recorded", "contradicted",
})


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _timestamp(value: datetime) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("occurred_at must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _receipt_document(receipt: EvidenceReceipt | None) -> dict[str, str] | None:
    if receipt is None:
        return None
    if not isinstance(receipt, EvidenceReceipt):
        raise TypeError("receipt must be an EvidenceReceipt")
    return {
        "execution_id": receipt.execution_id,
        "provider": receipt.provider,
        "action": receipt.action,
        "observed_at": receipt.observed_at,
        "mode": receipt.mode.value,
        "verification": receipt.verification.value,
        "policy_sha256": receipt.policy_sha256,
        "payload_sha256": receipt.payload_sha256,
        "result_sha256": receipt.result_sha256,
    }


class ReceiptLedger:
    """SQLite append-only event ledger with a verifiable SHA-256 hash chain."""

    def __init__(self, database: str | Path) -> None:
        self.database = str(database)
        if self.database == ":memory:":
            raise ValueError("use a file-backed SQLite database for durable ledger state")
        Path(self.database).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.database, timeout=10.0, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout = 10000")
        db.execute("PRAGMA journal_mode = WAL")
        return db

    def _initialize(self) -> None:
        with closing(self._connect()) as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS federation_receipt_ledger (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id TEXT NOT NULL,
                    event_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL UNIQUE
                )
            """)
            db.execute("""
                CREATE TRIGGER IF NOT EXISTS federation_ledger_no_update
                BEFORE UPDATE ON federation_receipt_ledger
                BEGIN SELECT RAISE(ABORT, 'federation ledger is append-only'); END
            """)
            db.execute("""
                CREATE TRIGGER IF NOT EXISTS federation_ledger_no_delete
                BEFORE DELETE ON federation_receipt_ledger
                BEGIN SELECT RAISE(ABORT, 'federation ledger is append-only'); END
            """)

    @staticmethod
    def _validate_details(details: Mapping[str, Any]) -> dict[str, str | int | float | bool | None]:
        if not isinstance(details, Mapping) or len(details) > 16:
            raise ValueError("details must be a mapping with at most 16 fields")
        safe: dict[str, str | int | float | bool | None] = {}
        for key, value in details.items():
            if not isinstance(key, str) or not key or len(key) > 64 or _SECRET_KEY.search(key):
                raise ValueError("details contain an unsafe field name")
            if isinstance(value, str):
                if len(value) > 200 or re.search(r"(?i)bearer\s+|access_token\s*[:=]", value):
                    raise ValueError("details contain an unsafe string value")
            elif value is not None and (isinstance(value, (dict, list)) or not isinstance(value, (int, float, bool))):
                raise ValueError("detail values must be bounded scalar values")
            if isinstance(value, float) and (value != value or abs(value) == float("inf")):
                raise ValueError("detail numbers must be finite")
            safe[key] = value
        return safe

    def append(
        self,
        *,
        execution_id: str,
        event_kind: str,
        occurred_at: datetime,
        details: Mapping[str, Any] | None = None,
        receipt: EvidenceReceipt | None = None,
    ) -> dict[str, Any]:
        """Append one immutable lifecycle fact and return its sequence/hash."""
        if not isinstance(execution_id, str) or not _EXECUTION_ID.fullmatch(execution_id):
            raise ValueError("execution_id is invalid")
        if event_kind not in _EVENT_KINDS:
            raise ValueError("unsupported event_kind")
        if (event_kind == "receipt_recorded") != (receipt is not None):
            raise ValueError("receipt is required only for receipt_recorded events")
        receipt_doc = _receipt_document(receipt)
        if receipt_doc is not None and receipt_doc["execution_id"] != execution_id:
            raise ValueError("receipt execution_id does not match ledger event")
        document = {
            "execution_id": execution_id,
            "event_kind": event_kind,
            "occurred_at": _timestamp(occurred_at),
            "details": self._validate_details(details or {}),
            "receipt": receipt_doc,
        }
        encoded = _canonical(document).decode("utf-8")
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT sequence, event_hash FROM federation_receipt_ledger ORDER BY sequence DESC LIMIT 1"
            ).fetchone()
            previous_hash = row["event_hash"] if row else _GENESIS
            sequence = (int(row["sequence"]) + 1) if row else 1
            event_hash = hashlib.sha256(_canonical({
                "sequence": sequence,
                "previous_hash": previous_hash,
                "event": document,
            })).hexdigest()
            db.execute(
                "INSERT INTO federation_receipt_ledger "
                "(sequence, execution_id, event_json, previous_hash, event_hash) VALUES (?, ?, ?, ?, ?)",
                (sequence, execution_id, encoded, previous_hash, event_hash),
            )
            db.execute("COMMIT")
        return {
            "sequence": sequence,
            "execution_id": execution_id,
            "event_kind": event_kind,
            "previous_hash": previous_hash,
            "event_hash": event_hash,
        }

    def verify_chain(self) -> dict[str, Any]:
        """Verify sequence continuity, canonical event bytes, and every link."""
        with closing(self._connect()) as db:
            rows = db.execute(
                "SELECT sequence, event_json, previous_hash, event_hash "
                "FROM federation_receipt_ledger ORDER BY sequence"
            ).fetchall()
        previous_hash = _GENESIS
        for expected_sequence, row in enumerate(rows, start=1):
            try:
                document = json.loads(row["event_json"])
                if _canonical(document).decode("utf-8") != row["event_json"]:
                    return {"valid": False, "checked": expected_sequence - 1, "reason": "non_canonical_event"}
                expected_hash = hashlib.sha256(_canonical({
                    "sequence": expected_sequence,
                    "previous_hash": previous_hash,
                    "event": document,
                })).hexdigest()
            except (TypeError, ValueError, json.JSONDecodeError):
                return {"valid": False, "checked": expected_sequence - 1, "reason": "invalid_event"}
            if int(row["sequence"]) != expected_sequence or row["previous_hash"] != previous_hash:
                return {"valid": False, "checked": expected_sequence - 1, "reason": "chain_link_mismatch"}
            if row["event_hash"] != expected_hash:
                return {"valid": False, "checked": expected_sequence - 1, "reason": "event_hash_mismatch"}
            previous_hash = expected_hash
        return {"valid": True, "checked": len(rows), "head_hash": previous_hash}

    def read(self, *, execution_id: str | None = None) -> list[dict[str, Any]]:
        """Return decoded events in append order, optionally scoped to one execution."""
        with closing(self._connect()) as db:
            if execution_id is None:
                rows = db.execute(
                    "SELECT sequence, event_json, previous_hash, event_hash "
                    "FROM federation_receipt_ledger ORDER BY sequence"
                ).fetchall()
            else:
                rows = db.execute(
                    "SELECT sequence, event_json, previous_hash, event_hash "
                    "FROM federation_receipt_ledger WHERE execution_id=? ORDER BY sequence",
                    (execution_id,),
                ).fetchall()
        return [
            {
                "sequence": int(row["sequence"]),
                "event": json.loads(row["event_json"]),
                "previous_hash": row["previous_hash"],
                "event_hash": row["event_hash"],
            }
            for row in rows
        ]
