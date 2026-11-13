"""Atomic durable operations for IXPANSION.

This adapter deliberately supports only Upstash Redis, whose REST API exposes
Redis commands and EVAL. Generic HTTP JSON stores are not assumed to provide
atomicity. No /tmp or GitHub fallback is permitted here.
"""
from __future__ import annotations

import hashlib
import json
import urllib.request
from typing import Any, Optional

from api import off_vercel_store


class AtomicStoreError(off_vercel_store.StoreError):
    """An atomic storage operation could not be completed."""


class AtomicStoreCapabilityError(AtomicStoreError):
    """The selected backend does not advertise the required atomic contract."""


_CAS_SCRIPT = """
local current = redis.call('GET', KEYS[1])
if ARGV[1] == 'MISSING' then
  if current then return 0 end
else
  if current ~= ARGV[1] then return 0 end
end
redis.call('SET', KEYS[1], ARGV[2])
return 1
"""

_APPEND_IDEMPOTENT_SCRIPT = """
local prior = redis.call('GET', KEYS[2])
if prior then return prior end
local event_id = redis.call('XADD', KEYS[1], '*', 'payload', ARGV[1])
redis.call('SET', KEYS[2], event_id, 'EX', ARGV[2])
return event_id
"""


class UpstashAtomicStore:
    """Small atomic primitive set backed by Redis server-side operations."""

    def __init__(self) -> None:
        if off_vercel_store.backend() != "upstash":
            raise AtomicStoreCapabilityError(
                "atomic operations require the configured Upstash Redis backend"
            )

    @staticmethod
    def _key(key: str) -> str:
        clean = off_vercel_store._key(key)
        return "ixpansion:atomic:" + clean

    @staticmethod
    def _command(*parts: Any) -> Any:
        url = off_vercel_store._upstash_url()
        token = off_vercel_store._upstash_token()
        request = urllib.request.Request(
            url + "/",
            data=json.dumps(list(parts), separators=(",", ":")).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        with off_vercel_store._open(request) as response:
            return off_vercel_store._read_response(response)

    def increment(self, key: str, amount: int = 1) -> int:
        """Atomically increment an integer counter."""
        if isinstance(amount, bool) or not isinstance(amount, int):
            raise TypeError("increment amount must be an integer")
        result = self._command("INCRBY", self._key(key), amount)
        if isinstance(result, bool) or not isinstance(result, int):
            raise AtomicStoreError("atomic increment returned a non-integer result")
        return result

    def compare_and_swap(
        self,
        key: str,
        expected: Any,
        replacement: Any,
        *,
        expect_missing: bool = False,
    ) -> bool:
        """Replace a JSON value only when its previous serialized value matches."""
        if expect_missing and expected is not None:
            raise ValueError("expected must be None when expect_missing=True")
        expected_raw = "MISSING" if expect_missing else json.dumps(
            expected, separators=(",", ":"), ensure_ascii=False
        )
        replacement_raw = json.dumps(
            replacement, separators=(",", ":"), ensure_ascii=False
        )
        result = self._command(
            "EVAL", _CAS_SCRIPT, 1, self._key(key),
            expected_raw, replacement_raw,
        )
        if result not in (0, 1):
            raise AtomicStoreError("compare-and-swap returned an invalid result")
        return result == 1

    def append_event(
        self,
        stream: str,
        event: Any,
        *,
        idempotency_key: Optional[str] = None,
        idempotency_ttl: int = 86400,
    ) -> str:
        """Append an event; optionally deduplicate retries for a bounded window."""
        payload = json.dumps(event, separators=(",", ":"), ensure_ascii=False)
        stream_key = self._key("stream:" + stream)
        if idempotency_key is None:
            result = self._command("XADD", stream_key, "*", "payload", payload)
        else:
            if not isinstance(idempotency_key, str) or not idempotency_key:
                raise ValueError("idempotency_key must be a non-empty string")
            if isinstance(idempotency_ttl, bool) or not isinstance(idempotency_ttl, int) or idempotency_ttl < 1:
                raise ValueError("idempotency_ttl must be a positive integer")
            digest = hashlib.sha256(
                (stream + "\0" + idempotency_key).encode("utf-8")
            ).hexdigest()
            result = self._command(
                "EVAL", _APPEND_IDEMPOTENT_SCRIPT, 2,
                stream_key, self._key("dedupe:" + digest),
                payload, idempotency_ttl,
            )
        if not isinstance(result, str) or not result:
            raise AtomicStoreError("event append returned an invalid stream ID")
        return result


def get_atomic_store() -> UpstashAtomicStore:
    """Return an atomic adapter or fail closed when capabilities are absent."""
    return UpstashAtomicStore()
