"""Tests for Wave 764 — creative_director."""
from __future__ import annotations

from api.wave764_creative_director import NAME, WAVE, coherence_vitals, handler, resonates_with


def test_contract():
    assert callable(handler) and callable(coherence_vitals)
    assert isinstance(resonates_with(), list)


def test_ping():
    assert handler({"action": "ping"})["ok"]


def test_status():
    out = handler({"action": "status"})
    assert out["ok"] and out["wave"] == WAVE


def test_inspire():
    out = handler({"action": "inspire"})
    assert out["ok"] and "inspiration" in out
    insp = out["inspiration"]
    assert "challenge" in insp and "organism_health" in insp


def test_task():
    out = handler({"action": "task"})
    assert out["ok"] and "task" in out
    task = out["task"]
    assert "text" in task and "difficulty" in task


def test_audit():
    out = handler({"action": "audit"})
    assert out["ok"] and "audit" in out
    audit = out["audit"]
    assert "harmony" in audit and "recommendations" in audit


def test_synthesize():
    out = handler({"action": "synthesize"})
    assert out["ok"] and "synthesis" in out


def test_unknown_action():
    assert handler({"action": "nope"})["ok"] is False


def test_coherence_vitals():
    v = coherence_vitals()
    assert v["wave"] == WAVE and v["status"] == "active"
