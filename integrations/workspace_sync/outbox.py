"""Durable, idempotent outbox for IXPANSION workspace synchronization.

Provider SDKs stay outside this package. Adapters are injected at runtime and
must implement idempotent delivery plus read-after-write verification.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
from contextlib import closing
from pathlib import Path
from typing import Any, Protocol

_SECRET_KEY = re.compile(r"(secret|token|password|passwd|authorization|api[_-]?key|private[_-]?key)", re.I)
_BEARER = re.compile(r"(?i)\b(bearer\s+)[A-Za-z0-9._~+/=-]+")
_KEY_VALUE = re.compile(r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]\s*[^\s,;]+")


class WorkspaceSyncError(Exception):
    """Base class for workspace synchronization errors."""


class IdempotencyConflict(WorkspaceSyncError):
    """A key was reused for a different operation or payload."""


class InvalidEvent(WorkspaceSyncError):
    """An event violates the workspace sync contract."""


class AdapterError(WorkspaceSyncError):
    """Base class for adapter delivery failures."""


class TransientAdapterError(AdapterError):
    """A retryable provider or transport failure."""


class PermanentAdapterError(AdapterError):
    """A non-retryable provider, policy, or validation failure."""


class Adapter(Protocol):
    def deliver(self, event: dict[str, Any]) -> dict[str, Any]:
        """Deliver an event; provider writes must honor event.idempotency_key."""

    def verify(self, event: dict[str, Any], receipt: dict[str, Any]) -> bool:
        """Read the destination back and verify the expected artifact."""


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _payload_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def _check_payload(value: Any, path: str = "payload") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if _SECRET_KEY.search(str(key)):
                raise InvalidEvent(f"credential-like field is not allowed: {path}.{key}")
            _check_payload(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _check_payload(child, f"{path}[{index}]")
    elif isinstance(value, (str, int, float, bool)) or value is None:
        return
    else:
        raise InvalidEvent(f"unsupported payload value at {path}: {type(value).__name__}")


def _redact_error(error: str) -> str:
    text = _BEARER.sub(r"\1[REDACTED]", str(error))
    text = _KEY_VALUE.sub(r"\1=[REDACTED]", text)
    return text[:500]


class WorkspaceOutbox:
    """SQLite-backed durable queue with leases and idempotency enforcement."""

    def __init__(self, database: str | Path, *, retry_base_seconds: float = 5.0,
                 retry_max_seconds: float = 3600.0) -> None:
        self.database = str(database)
        if self.database == ":memory:":
            raise ValueError("use a file-backed SQLite database for durable multi-connection outbox state")
        self.retry_base_seconds = max(0.1, float(retry_base_seconds))
        self.retry_max_seconds = max(self.retry_base_seconds, float(retry_max_seconds))
        if self.database != ":memory:":
            Path(self.database).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.database, timeout=10.0, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout = 10000")
        if self.database != ":memory:":
            db.execute("PRAGMA journal_mode = WAL")
        return db

    def _initialize(self) -> None:
        with closing(self._connect()) as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS workspace_outbox (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    source TEXT NOT NULL,
                    target TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_hash TEXT NOT NULL,
                    idempotent INTEGER NOT NULL CHECK (idempotent IN (0, 1)),
                    state TEXT NOT NULL CHECK (state IN ('pending','inflight','delivered','dead')),
                    attempts INTEGER NOT NULL DEFAULT 0,
                    next_attempt_at REAL NOT NULL,
                    lease_until REAL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    last_error TEXT
                )
            """)
            db.execute("CREATE INDEX IF NOT EXISTS idx_workspace_outbox_due ON workspace_outbox(state, next_attempt_at)")

    def enqueue(self, *, idempotency_key: str, source: str, target: str,
                operation: str, payload: dict[str, Any], idempotent: bool = True,
                now: float | None = None) -> bool:
        """Insert once. Return False for an exact replay; reject key collisions."""
        if not isinstance(idempotency_key, str) or not idempotency_key.strip() or len(idempotency_key) > 200:
            raise InvalidEvent("idempotency_key must be 1..200 characters")
        for name, value in (("source", source), ("target", target), ("operation", operation)):
            if not isinstance(value, str) or not value.strip() or len(value) > 120:
                raise InvalidEvent(f"{name} must be 1..120 characters")
        if not isinstance(payload, dict):
            raise InvalidEvent("payload must be an object")
        _check_payload(payload)
        timestamp = time.time() if now is None else float(now)
        digest = _payload_hash(payload)
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT source,target,operation,payload_hash,idempotent FROM workspace_outbox WHERE idempotency_key=?",
                (idempotency_key,),
            ).fetchone()
            if row:
                same = (
                    row["source"] == source and row["target"] == target
                    and row["operation"] == operation and row["payload_hash"] == digest
                    and bool(row["idempotent"]) == bool(idempotent)
                )
                db.execute("COMMIT")
                if not same:
                    raise IdempotencyConflict(f"idempotency key reused with different content: {idempotency_key}")
                return False
            db.execute("""
                INSERT INTO workspace_outbox
                (idempotency_key,source,target,operation,payload_json,payload_hash,idempotent,
                 state,attempts,next_attempt_at,created_at,updated_at)
                VALUES (?,?,?,?,?,?,?,'pending',0,?,?,?)
            """, (idempotency_key, source, target, operation,
                  json.dumps(payload, sort_keys=True, separators=(",", ":")),
                  digest, int(bool(idempotent)), timestamp, timestamp, timestamp))
            db.execute("COMMIT")
        return True

    def preview_due(self, *, now: float | None = None, limit: int = 10) -> list[dict[str, Any]]:
        """Inspect due work without claiming it or changing durable state."""
        timestamp = time.time() if now is None else float(now)
        batch = max(1, min(int(limit), 100))
        with closing(self._connect()) as db:
            rows = db.execute("""
                SELECT event_id,idempotency_key,target,operation,attempts
                FROM workspace_outbox WHERE state='pending' AND next_attempt_at <= ?
                ORDER BY event_id LIMIT ?
            """, (timestamp, batch)).fetchall()
        return [dict(row) for row in rows]

    def claim_due(self, *, now: float | None = None, lease_seconds: float = 60.0,
                  limit: int = 10) -> list[dict[str, Any]]:
        """Claim due work atomically; expired non-idempotent leases become dead."""
        timestamp = time.time() if now is None else float(now)
        lease = max(1.0, float(lease_seconds))
        batch = max(1, min(int(limit), 100))
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("""
                UPDATE workspace_outbox
                SET state=CASE WHEN idempotent=1 THEN 'pending' ELSE 'dead' END,
                    lease_until=NULL,
                    next_attempt_at=CASE WHEN idempotent=1 THEN ? ELSE next_attempt_at END,
                    updated_at=?,
                    last_error=CASE WHEN idempotent=1 THEN 'lease expired; safe replay' ELSE 'lease expired; delivery outcome uncertain' END
                WHERE state='inflight' AND lease_until <= ?
            """, (timestamp, timestamp, timestamp))
            rows = db.execute("""
                SELECT * FROM workspace_outbox
                WHERE state='pending' AND next_attempt_at <= ?
                ORDER BY event_id LIMIT ?
            """, (timestamp, batch)).fetchall()
            claimed: list[dict[str, Any]] = []
            for row in rows:
                db.execute("""
                    UPDATE workspace_outbox SET state='inflight', attempts=attempts+1,
                        lease_until=?, updated_at=? WHERE event_id=? AND state='pending'
                """, (timestamp + lease, timestamp, row["event_id"]))
                item = dict(row)
                item["state"] = "inflight"
                item["attempts"] = int(row["attempts"]) + 1
                item["lease_until"] = timestamp + lease
                item["payload"] = json.loads(row["payload_json"])
                claimed.append(item)
            db.execute("COMMIT")
        return claimed

    def mark_delivered(self, event_id: int, *, now: float | None = None) -> None:
        timestamp = time.time() if now is None else float(now)
        with closing(self._connect()) as db:
            cursor = db.execute("""
                UPDATE workspace_outbox SET state='delivered', lease_until=NULL,
                    updated_at=?, last_error=NULL WHERE event_id=? AND state='inflight'
            """, (timestamp, int(event_id)))
            if cursor.rowcount != 1:
                raise WorkspaceSyncError(f"event is not inflight: {event_id}")

    def mark_failed(self, event_id: int, error: str, *, transient: bool,
                    now: float | None = None) -> str:
        timestamp = time.time() if now is None else float(now)
        with closing(self._connect()) as db:
            row = db.execute(
                "SELECT attempts,idempotent FROM workspace_outbox WHERE event_id=? AND state='inflight'",
                (int(event_id),),
            ).fetchone()
            if row is None:
                raise WorkspaceSyncError(f"event is not inflight: {event_id}")
            retry = bool(transient and row["idempotent"])
            if retry:
                delay = min(self.retry_max_seconds, self.retry_base_seconds * (2 ** max(0, int(row["attempts"]) - 1)))
                state, next_at = "pending", timestamp + delay
            else:
                state, next_at = "dead", timestamp
            db.execute("""
                UPDATE workspace_outbox SET state=?, next_attempt_at=?, lease_until=NULL,
                    updated_at=?, last_error=? WHERE event_id=?
            """, (state, next_at, timestamp, _redact_error(error), int(event_id)))
        return state

    def get(self, event_id: int) -> dict[str, Any] | None:
        with closing(self._connect()) as db:
            row = db.execute("SELECT * FROM workspace_outbox WHERE event_id=?", (int(event_id),)).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["payload"] = json.loads(item["payload_json"])
        return item

    def stats(self) -> dict[str, int]:
        with closing(self._connect()) as db:
            rows = db.execute("SELECT state, COUNT(*) AS n FROM workspace_outbox GROUP BY state").fetchall()
        counts = {row["state"]: int(row["n"]) for row in rows}
        return {state: counts.get(state, 0) for state in ("pending", "inflight", "delivered", "dead")}


class WorkspaceSyncRunner:
    """Dispatch through injected provider adapters; never assumes delivery is verified."""

    def __init__(self, outbox: WorkspaceOutbox, adapters: dict[str, Adapter]) -> None:
        self.outbox = outbox
        self.adapters = dict(adapters)

    def run_once(self, *, now: float | None = None, limit: int = 10,
                 dry_run: bool = False) -> list[dict[str, Any]]:
        if dry_run:
            return [{"state": "would_dispatch", **item}
                    for item in self.outbox.preview_due(now=now, limit=limit)]
        outcomes: list[dict[str, Any]] = []
        for event in self.outbox.claim_due(now=now, limit=limit):
            adapter = self.adapters.get(event["target"])
            if adapter is None:
                state = self.outbox.mark_failed(event["event_id"], "no adapter registered", transient=False, now=now)
                outcomes.append({"event_id": event["event_id"], "state": state, "reason": "adapter_missing"})
                continue
            try:
                receipt = adapter.deliver(event)
                if not isinstance(receipt, dict) or not adapter.verify(event, receipt):
                    raise PermanentAdapterError("destination read-after-write verification failed")
                self.outbox.mark_delivered(event["event_id"], now=now)
                outcomes.append({"event_id": event["event_id"], "state": "delivered_verified"})
            except TransientAdapterError as exc:
                state = self.outbox.mark_failed(event["event_id"], str(exc), transient=True, now=now)
                outcomes.append({"event_id": event["event_id"], "state": state, "reason": "transient_adapter_error"})
            except Exception as exc:
                state = self.outbox.mark_failed(event["event_id"], str(exc), transient=False, now=now)
                outcomes.append({"event_id": event["event_id"], "state": state, "reason": "permanent_or_unclassified_error"})
        return outcomes
