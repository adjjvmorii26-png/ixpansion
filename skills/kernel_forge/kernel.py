"""Small deterministic kernel for compacting duplicate JSON records.

The function is deliberately pure: it performs no I/O, network access, or writes.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from collections.abc import Iterable, Mapping
from typing import Any


class KernelInputError(ValueError):
    """Input does not satisfy the kernel contract."""


class KernelConflictError(KernelInputError):
    """A stable identity was reused for different content."""


class KernelLimitError(KernelInputError):
    """The input exceeds a declared resource limit."""


@dataclass(frozen=True)
class CompactionResult:
    records: tuple[dict[str, Any], ...]
    duplicate_count: int
    byte_count: int
    digest: str


def _positive_limit(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise KernelInputError(f"{name} must be a positive integer")
    return value


def _canonical_record(record: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    if not isinstance(record, Mapping):
        raise KernelInputError("each record must be a JSON object")
    identity = record.get("id")
    if not isinstance(identity, str) or not identity.strip():
        raise KernelInputError("each record must have a non-empty string id")
    try:
        canonical = json.dumps(
            dict(record),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        normalized = json.loads(canonical)
    except (TypeError, ValueError) as exc:
        raise KernelInputError(f"record is not valid finite JSON: {exc}") from exc
    return canonical, normalized


def compact_records(
    records: Iterable[Mapping[str, Any]],
    *,
    max_items: int = 512,
    max_bytes: int = 262_144,
) -> CompactionResult:
    """Deduplicate exact records by id, preserving first-seen order.

    Reusing an id for different content is a conflict, not a last-write-wins
    update. Limits are checked before returning, so callers never receive a
    silently truncated result.
    """
    item_limit = _positive_limit(max_items, "max_items")
    byte_limit = _positive_limit(max_bytes, "max_bytes")

    unique: list[dict[str, Any]] = []
    canonical_by_id: dict[str, str] = {}
    canonical_lines: list[str] = []
    byte_count = 0
    duplicate_count = 0

    for record in records:
        canonical, normalized = _canonical_record(record)
        identity = normalized["id"]
        previous = canonical_by_id.get(identity)

        if previous is not None:
            if previous != canonical:
                raise KernelConflictError(
                    f"identity {identity!r} maps to conflicting content"
                )
            duplicate_count += 1
            continue

        next_count = len(unique) + 1
        next_bytes = byte_count + len(canonical.encode("utf-8"))
        if next_count > item_limit:
            raise KernelLimitError(f"item limit exceeded: {item_limit}")
        if next_bytes > byte_limit:
            raise KernelLimitError(f"byte limit exceeded: {byte_limit}")

        canonical_by_id[identity] = canonical
        unique.append(normalized)
        canonical_lines.append(canonical)
        byte_count = next_bytes

    payload = "\n".join(canonical_lines).encode("utf-8")
    return CompactionResult(
        records=tuple(unique),
        duplicate_count=duplicate_count,
        byte_count=byte_count,
        digest=hashlib.sha256(payload).hexdigest(),
    )
