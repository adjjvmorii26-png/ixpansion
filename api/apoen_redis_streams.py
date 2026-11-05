"""APOEN-0 Redis Streams ingress adapter.
Uses a redis-py-compatible xread method. It never acknowledges, deletes,
trims, or mutates stream entries. Redis remains an optional external service.
"""
from __future__ import annotations
import re
from typing import Any, Mapping
from api.apoen_somatic_gc import SomaticGarbageCollector

_REQUIRED = ("branch_id", "cluster_id", "created_at", "last_heartbeat", "interaction_count", "signature")
_SIGNATURE = re.compile(r"^[0-9a-f]{64}$")

def _text(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="strict")
    if isinstance(value, str):
        return value
    raise ValueError("stream field must be text or UTF-8 bytes")

def _integer(value: Any, field: str) -> int:
    raw = _text(value)
    if not raw.isascii() or not raw.isdecimal():
        raise ValueError(f"{field} must be a non-negative integer")
    return int(raw)

def read_heartbeats(client: Any, stream: str, *, last_id: str = "$", count: int = 50, block_ms: int = 1000) -> list[dict[str, Any]]:
    """Read a bounded batch of heartbeat events without changing Redis state."""
    if not isinstance(stream, str) or not stream:
        raise ValueError("stream must be non-empty")
    if not isinstance(last_id, str) or not last_id:
        raise ValueError("last_id must be non-empty")
    if type(count) is not int or not 1 <= count <= 500:
        raise ValueError("count must be between 1 and 500")
    if type(block_ms) is not int or not 0 <= block_ms <= 5000:
        raise ValueError("block_ms must be between 0 and 5000")
    response = client.xread({stream: last_id}, count=count, block=block_ms)
    if not isinstance(response, (list, tuple)):
        raise ValueError("Redis xread response must be a sequence")
    records: list[dict[str, Any]] = []
    for stream_name, entries in response:
        if _text(stream_name) != stream:
            raise ValueError("Redis returned an unexpected stream")
        if not isinstance(entries, (list, tuple)):
            raise ValueError("Redis stream entries must be a sequence")
        for entry_id, fields in entries:
            if not isinstance(fields, Mapping):
                raise ValueError("Redis stream fields must be a mapping")
            decoded = {_text(key): value for key, value in fields.items()}
            missing = [key for key in _REQUIRED if key not in decoded]
            if missing:
                raise ValueError(f"heartbeat missing fields: {','.join(missing)}")
            signature = _text(decoded["signature"])
            if not _SIGNATURE.fullmatch(signature):
                raise ValueError("heartbeat signature must be 64 lowercase hex characters")
            payload = {
                "branch_id": _text(decoded["branch_id"]),
                "cluster_id": _text(decoded["cluster_id"]),
                "created_at": _integer(decoded["created_at"], "created_at"),
                "last_heartbeat": _integer(decoded["last_heartbeat"], "last_heartbeat"),
                "interaction_count": _integer(decoded["interaction_count"], "interaction_count"),
            }
            if not payload["branch_id"] or not payload["cluster_id"]:
                raise ValueError("branch_id and cluster_id must be non-empty")
            records.append({"stream": stream, "stream_id": _text(entry_id), "heartbeat_payload": payload, "signature": signature})
            if len(records) > count:
                raise ValueError("Redis returned more entries than requested")
    return records

def evaluate_heartbeats(collector: SomaticGarbageCollector, records: list[Mapping[str, Any]], secret: bytes, *, now: int) -> list[dict[str, Any]]:
    """Evaluate authenticated stream records; never performs pruning."""
    results = []
    for record in records:
        payload = record["heartbeat_payload"]
        branch_id = payload.get("branch_id")
        metadata = {key: payload.get(key) for key in ("created_at", "last_heartbeat", "interaction_count")}
        evaluation = collector.evaluate_authenticated_branch(branch_id, metadata, payload, record.get("signature"), secret, now=now)
        results.append({"stream": record.get("stream"), "stream_id": record.get("stream_id"), "evaluation": evaluation, "destructive_action_performed": False})
    return results
