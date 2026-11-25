"""Tests for wave981 still_residue — pure, no network."""
from __future__ import annotations

from api.wave981_still_residue import evaluate, still_residue, handler, coherence_vitals


def test_residue_length_and_type():
    r = evaluate({"hush_score": 0.9})
    assert len(r["residue"]) == 8
    assert r["product_surface"] == "hush"
    assert r["bytes_kept"] == 8


def test_high_hush_more_still():
    high = still_residue(0.95)
    low = still_residue(0.05)
    assert high.count("0") >= low.count("0")


def test_handler_and_vitals():
    v = coherence_vitals()
    assert v["wave"] == 981
    assert v["ok"] is True
    h = handler({"action": "status"})
    assert h["status"] == "active"
    h2 = handler({"hush_score": 0.7})
    assert h2["status"] == "residued"
    assert "residue" in h2


def test_deterministic():
    a = evaluate({"hush_score": 0.42, "salt": "x"})
    b = evaluate({"hush_score": 0.42, "salt": "x"})
    assert a["residue"] == b["residue"]
