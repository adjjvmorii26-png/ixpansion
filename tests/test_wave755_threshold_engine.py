"""Tests for Wave 755 — threshold_engine."""
from __future__ import annotations

from api.wave755_threshold_engine import NAME, WAVE, coherence_vitals, handler, resonates_with


def test_contract():
    assert callable(handler)
    assert callable(coherence_vitals)
    assert isinstance(resonates_with(), list)


def test_ping():
    out = handler({"action": "ping"})
    assert out["ok"] and out["alive"]


def test_status():
    out = handler({"action": "status"})
    assert out["ok"] and out["wave"] == WAVE and out["name"] == NAME


def test_probe():
    out = handler({"action": "probe", "drift": 0.7, "entropy": 0.6, "coherence": 0.8})
    assert out["ok"] and 0 < out["readiness"] <= 1
    assert out["threshold"] in ("deep_root", "stabilizing", "approaching_boundary", "transcendence_ready")


def test_readiness():
    out = handler({"action": "readiness"})
    assert out["ok"] and "score" in out and "next_boundary" in out


def test_cross_denied_below_threshold():
    out = handler({"action": "cross"})
    assert out["ok"] is False and out["reason"] == "readiness_below_threshold"


def test_cross_allowed():
    for _ in range(10):
        handler({"action": "probe", "drift": 0.9, "entropy": 0.9, "coherence": 0.9})
    out = handler({"action": "cross"})
    assert out["ok"] and out["crossed"] is True


def test_unknown_action():
    out = handler({"action": "nope"})
    assert out["ok"] is False and out["error"] == "unknown_action"


def test_coherence_vitals():
    v = coherence_vitals()
    assert v["wave"] == WAVE and v["status"] == "active"
