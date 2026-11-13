"""SquirrelCache: bounded, process-safe SQLite cache for ephemeral acceleration.

This cache is never an authority for durable state. Callers must fetch from the
configured durable store on a miss, and cache hits must not be used as proof of
identity, authorization, or integrity.
"""
from __future__ import annotations

import json
from contextlib import closing
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Optional, Tuple


DEFAULT_PATH = "/tmp/ixp_squirrel_cache.sqlite3"
DEFAULT_MAX_ENTRIES = 512
DEFAULT_MAX_BYTES = 8 * 1024 * 1024


def _settings(path=None, max_entries=None, max_bytes=None):
    selected_path = path or os.environ.get("IXP_SQUIRREL_CACHE_PATH") or DEFAULT_PATH
    entries = max_entries if max_entries is not None else int(
        os.environ.get("IXP_SQUIRREL_CACHE_MAX_ENTRIES", DEFAULT_MAX_ENTRIES)
    )
    byte_limit = max_bytes if max_bytes is not None else int(
        os.environ.get("IXP_SQUIRREL_CACHE_MAX_BYTES", DEFAULT_MAX_BYTES)
    )
    if entries < 1 or byte_limit < 1:
        raise ValueError("SquirrelCache limits must be positive")
    return str(selected_path), entries, byte_limit


class SquirrelCache:
    """A bounded TTL/LRU JSON cache backed by SQLite transactions."""

    def __init__(
        self,
        path: Optional[str] = None,
        max_entries: Optional[int] = None,
        max_bytes: Optional[int] = None,
    ):
        self.path, self.max_entries, self.max_bytes = _settings(
            path, max_entries, max_bytes
        )
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS cache_entries (
                    cache_key TEXT PRIMARY KEY,
                    payload BLOB NOT NULL,
                    expires_at REAL NOT NULL,
                    touched_at REAL NOT NULL,
                    byte_size INTEGER NOT NULL
                )
                """
            )
            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_cache_expiry "
                "ON cache_entries(expires_at)"
            )

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=5.0, isolation_level=None)
        db.execute("PRAGMA busy_timeout=5000")
        db.execute("PRAGMA journal_mode=WAL")
        return db

    def get(self, key: str, now: Optional[float] = None) -> Tuple[bool, Any]:
        if not isinstance(key, str) or not key:
            raise ValueError("cache key must be a non-empty string")
        current = time.time() if now is None else float(now)
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM cache_entries WHERE expires_at <= ?", (current,))
            row = db.execute(
                "SELECT payload FROM cache_entries "
                "WHERE cache_key = ? AND expires_at > ?",
                (key, current),
            ).fetchone()
            if row is None:
                db.execute("COMMIT")
                return False, None
            db.execute(
                "UPDATE cache_entries SET touched_at = ? WHERE cache_key = ?",
                (current, key),
            )
            db.execute("COMMIT")
        try:
            return True, json.loads(bytes(row[0]).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self.delete(key)
            raise ValueError("SquirrelCache contains invalid JSON") from exc

    def put(
        self,
        key: str,
        value: Any,
        ttl: float,
        now: Optional[float] = None,
    ) -> bool:
        if not isinstance(key, str) or not key:
            raise ValueError("cache key must be a non-empty string")
        if ttl <= 0:
            self.delete(key)
            return False
        current = time.time() if now is None else float(now)
        payload = json.dumps(
            value, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        size = len(payload)
        if size > self.max_bytes:
            self.delete(key)
            return False

        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM cache_entries WHERE expires_at <= ?", (current,))
            db.execute(
                """
                INSERT INTO cache_entries
                    (cache_key, payload, expires_at, touched_at, byte_size)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    payload=excluded.payload,
                    expires_at=excluded.expires_at,
                    touched_at=excluded.touched_at,
                    byte_size=excluded.byte_size
                """,
                (key, payload, current + float(ttl), current, size),
            )
            while True:
                count, total = db.execute(
                    "SELECT COUNT(*), COALESCE(SUM(byte_size), 0) FROM cache_entries"
                ).fetchone()
                if count <= self.max_entries and total <= self.max_bytes:
                    break
                db.execute(
                    "DELETE FROM cache_entries WHERE cache_key = "
                    "(SELECT cache_key FROM cache_entries "
                    "ORDER BY touched_at ASC, cache_key ASC LIMIT 1)"
                )
            db.execute("COMMIT")
        return True

    def delete(self, key: str) -> None:
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM cache_entries WHERE cache_key = ?", (key,))
            db.execute("COMMIT")

    def clear(self) -> None:
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM cache_entries")
            db.execute("COMMIT")

    def stats(self) -> dict:
        with closing(self._connect()) as db:
            count, total = db.execute(
                "SELECT COUNT(*), COALESCE(SUM(byte_size), 0) FROM cache_entries"
            ).fetchone()
        return {
            "entries": count,
            "bytes": total,
            "max_entries": self.max_entries,
            "max_bytes": self.max_bytes,
            "durable": False,
            "authority": False,
        }
