"""Tests for context.compact — pure, no network."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from context.compact import (
    ArtifactError,
    bind,
    content_hash,
    forget,
    load_jsonl,
    pack,
    promote_residue_to_seed,
    to_line,
    validate,
)


def test_validate_rejects_bad_kind():
    with pytest.raises(ArtifactError):
        validate({"kind": "note", "id": "x", "t": "2026-01-01"})


def test_bind_dedupes_and_conflicts():
    a = {"kind": "seed", "id": "s1", "t": "2026-01-01", "body": {"intent": "a"}}
    b = {"kind": "seed", "id": "s1", "t": "2026-01-02", "body": {"intent": "a"}}
    c = {"kind": "seed", "id": "s1", "t": "2026-01-03", "body": {"intent": "other"}}
    assert len(bind([a, b])) == 1
    with pytest.raises(ArtifactError, match="conflict"):
        bind([a, c])


def test_forget_ttl():
    pulse = {"kind": "pulse", "id": "p1", "t": "2026-01-01", "ttl_days": 7, "body": {}}
    seed = {"kind": "seed", "id": "s1", "t": "2026-01-01", "ttl_days": 0, "body": {"intent": "x"}}
    assert [r["id"] for r in forget([pulse, seed], today=date(2026, 1, 20))] == ["s1"]


def test_pack_priority():
    rows = [
        {"kind": "residue", "id": "r1", "t": "2026-01-01", "body": {"lesson": "L" * 40}},
        {"kind": "seed", "id": "s1", "t": "2026-01-01", "body": {"intent": "keep"}},
    ]
    text = pack(rows, budget_tokens=80)
    assert text.startswith("# ixpansion-context")
    assert "seed|" in text


def test_promote_residue():
    seed = promote_residue_to_seed({
        "kind": "residue", "id": "res1", "t": "2026-02-01",
        "body": {"lesson": "pin runners"},
    })
    assert seed["kind"] == "seed" and "pin runners" in seed["body"]["intent"]


def test_ledger_loads():
    path = Path(__file__).resolve().parents[1] / "context" / "ledger.jsonl"
    rows = load_jsonl(path)
    assert len(rows) >= 5
    assert "seed" in pack(rows, budget_tokens=500)


def test_content_hash_stable():
    r = {"kind": "receipt", "id": "x", "t": "2026-01-01", "body": {"act": "m"}}
    assert content_hash(r) == content_hash(dict(r))


def test_to_line_escapes_pipes():
    assert "a/b" in to_line({"kind": "seed", "id": "s", "t": "2026-01-01", "body": {"intent": "a|b"}})
