\"\"\"Tests for context.compact — pure, no network.\"\"\"
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from context.compact import (
    ArtifactError,
    append_jsonl,
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
    out = bind([a, b])
    assert len(out) == 1
    with pytest.raises(ArtifactError, match="conflict"):
        bind([a, c])


def test_forget_ttl():
    pulse = {"kind": "pulse", "id": "p1", "t": "2026-01-01", "ttl_days": 7, "body": {}}
    seed = {"kind": "seed", "id": "s1", "t": "2026-01-01", "ttl_days": 0, "body": {"intent": "x"}}
    kept = forget([pulse, seed], today=date(2026, 1, 20))
    assert [r["id"] for r in kept] == ["s1"]


def test_pack_respects_budget_and_priority():
    rows = [
        {"kind": "residue", "id": "r1", "t": "2026-01-01", "body": {"lesson": "L" * 50}},
        {"kind": "seed", "id": "s1", "t": "2026-01-01", "body": {"intent": "keep"}},
        {"kind": "pulse", "id": "p1", "t": "2026-01-01", "ttl_days": 30, "body": {"health": "ok"}},
    ]
    text = pack(rows, budget_tokens=80)
    assert "seed|" in text
    assert text.startswith("# ixpansion-context")


def test_promote_residue():
    res = {
        "kind": "residue",
        "id": "res1",
        "t": "2026-02-01",
        "body": {"lesson": "pin runners"},
    }
    seed = promote_residue_to_seed(res)
    assert seed["kind"] == "seed"
    assert seed["ttl_days"] == 0
    assert "pin runners" in seed["body"]["intent"]


def test_ledger_loads():
    path = Path(__file__).resolve().parents[1] / "context" / "ledger.jsonl"
    rows = load_jsonl(path)
    assert len(rows) >= 5
    text = pack(rows, budget_tokens=500)
    assert "seed:silence" in text or "silence" in text


def test_content_hash_stable():
    r = {"kind": "receipt", "id": "x", "t": "2026-01-01", "body": {"act": "m"}}
    assert content_hash(r) == content_hash(dict(r))


def test_to_line_no_pipes_in_values():
    r = {"kind": "seed", "id": "s", "t": "2026-01-01", "body": {"intent": "a|b"}}
    line = to_line(r)
    assert line.count("|") >= 3
    assert "a/b" in line
