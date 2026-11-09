from __future__ import annotations

import pytest

from skills.kernel_forge.kernel import (
    KernelConflictError,
    KernelInputError,
    KernelLimitError,
    compact_records,
)


def test_compaction_removes_exact_duplicates_and_preserves_first_seen_order():
    result = compact_records([
        {"id": "a", "value": 1},
        {"id": "b", "value": 2},
        {"value": 1, "id": "a"},
    ])

    assert [item["id"] for item in result.records] == ["a", "b"]
    assert result.duplicate_count == 1
    assert result.byte_count > 0
    assert len(result.digest) == 64


def test_compaction_digest_is_independent_of_mapping_key_order():
    left = compact_records([{"id": "a", "value": 1, "meta": {"z": 2, "a": 1}}])
    right = compact_records([{"meta": {"a": 1, "z": 2}, "value": 1, "id": "a"}])

    assert left.digest == right.digest


def test_conflicting_content_for_same_identity_fails_closed():
    with pytest.raises(KernelConflictError):
        compact_records([{"id": "same", "value": 1}, {"id": "same", "value": 2}])


@pytest.mark.parametrize("record", [{}, {"id": ""}, {"id": 7}, {"id": "x", "bad": float("nan")}])
def test_invalid_records_are_rejected(record):
    with pytest.raises(KernelInputError):
        compact_records([record])


def test_item_limit_rejects_instead_of_silently_truncating():
    with pytest.raises(KernelLimitError):
        compact_records([{"id": "a"}, {"id": "b"}], max_items=1)


def test_byte_limit_rejects_instead_of_silently_truncating():
    with pytest.raises(KernelLimitError):
        compact_records([{"id": "a", "value": "payload"}], max_bytes=4)


@pytest.mark.parametrize("limit", [0, -1, True, 1.5])
def test_limits_must_be_positive_integers(limit):
    with pytest.raises(KernelInputError):
        compact_records([], max_items=limit)
