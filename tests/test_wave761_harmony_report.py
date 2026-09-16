"""Tests for Wave 761 — harmony_report."""
from __future__ import annotations

from api.wave761_harmony_report import NAME, WAVE, coherence_vitals, handler, resonates_with


def test_contract():
    assert callable(handler) and callable(coherence_vitals)
    assert isinstance(resonates_with(), list)


def test_ping():
    assert handler({"action": "ping"})["ok"]


def test_status():
    out = handler({"action": "status"})
    assert out["ok"] and out["wave"] == WAVE


def test_aggregate():
    out = handler({"action": "aggregate"})
    assert out["ok"]
    assert out["organs"] >= 5
    assert 0 <= out["avg_resonance"] <= 1
    assert "healthy" in out and "fragile" in out


def test_health():
    handler({"action": "aggregate"})
    out = handler({"action": "health"})
    assert out["ok"] and out["label"] in ("thriving", "stable", "fragile", "critical")


def test_health_no_data():
    import json
    from pathlib import Path
    Path("data/wave761_harmony_report.json").write_text(json.dumps({"wave": 761, "name": "harmony_report", "snapshots": [], "status": "seed"}))
    out = handler({"action": "health"})
    assert out["ok"] and out["status"] == "no_data"
    # Re-aggregate for other tests
    handler({"action": "aggregate"})


def test_topology():
    out = handler({"action": "topology"})
    assert out["ok"] and out["total_organs"] >= 5
    assert "layers" in out


def test_unknown_action():
    assert handler({"action": "nope"})["ok"] is False


def test_coherence_vitals():
    v = coherence_vitals()
    assert v["wave"] == WAVE and v["status"] == "active"
