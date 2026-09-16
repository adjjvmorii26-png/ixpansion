"""Tests for Wave 758 — continuity_weaver."""
from __future__ import annotations

from api.wave758_continuity_weaver import NAME, WAVE, coherence_vitals, handler, resonates_with


def test_contract():
    assert callable(handler) and callable(coherence_vitals)
    assert isinstance(resonates_with(), list)


def test_ping():
    assert handler({"action": "ping"})["ok"]


def test_status():
    out = handler({"action": "status"})
    assert out["ok"] and out["wave"] == WAVE


def test_braid():
    out = handler({"action": "braid", "name": "dream-thread", "strength": 0.8})
    assert out["ok"] and out["health"] == "strong"


def test_repair():
    handler({"action": "braid", "name": "fragile-one", "strength": 0.1})
    before = handler({"action": "deltas"})["threads"]
    frag = next(t for t in before if t["name"] == "fragile-one")
    out = handler({"action": "repair", "name": "fragile-one"})
    assert out["ok"] and out["new_strength"] >= frag["strength"]


def test_repair_missing():
    out = handler({"action": "repair", "name": "nope"})
    assert out["ok"] is False and out["error"] == "thread_not_found"


def test_deltas():
    handler({"action": "braid", "name": "x", "strength": 0.5})
    out = handler({"action": "deltas"})
    assert out["ok"] and len(out["threads"]) >= 1
    assert "health" in out["threads"][0]


def test_unknown_action():
    assert handler({"action": "nope"})["ok"] is False


def test_coherence_vitals():
    v = coherence_vitals()
    assert v["wave"] == WAVE and v["status"] == "active"
