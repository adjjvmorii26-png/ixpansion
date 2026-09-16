"""Tests for Wave 762 — dream_compiler."""
from __future__ import annotations

from api.wave762_dream_compiler import NAME, WAVE, coherence_vitals, handler, resonates_with


def test_contract():
    assert callable(handler) and callable(coherence_vitals)
    assert isinstance(resonates_with(), list)


def test_ping():
    assert handler({"action": "ping"})["ok"]


def test_status():
    out = handler({"action": "status"})
    assert out["ok"] and out["wave"] == WAVE


def test_dream():
    out = handler({"action": "dream"})
    assert out["ok"] and "dream" in out
    dream = out["dream"]
    assert "name" in dream and "purpose" in dream and "actions" in dream
    assert dream["validation"]["valid"] or not dream["validation"]["valid"]


def test_draft():
    out = handler({"action": "draft"})
    assert out["ok"] and "code_length" in out
    assert out["code_length"] > 100


def test_birth():
    handler({"action": "dream"})
    out = handler({"action": "birth"})
    assert out["ok"] and "born" in out
    assert "path" in out["born"]


def test_birth_no_dreams():
    import json
    from pathlib import Path
    Path("data/wave762_dream_compiler.json").write_text(
        json.dumps({"wave": 762, "name": "dream_compiler", "dreams": [], "births": [], "status": "seed"}))
    out = handler({"action": "birth"})
    assert out["ok"] is False and out["error"] == "no_dreams_to_birth"
    handler({"action": "dream"})


def test_unknown_action():
    assert handler({"action": "nope"})["ok"] is False


def test_coherence_vitals():
    v = coherence_vitals()
    assert v["wave"] == WAVE and v["status"] == "active"
