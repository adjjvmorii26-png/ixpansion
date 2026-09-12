"""Tests for Wave 425 Quantum Superposition."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave425_superposition as ws

def test_superpose():
    qs = ws.superpose()
    assert qs["module"] == "wave425_superposition"
    assert qs["superposed"] is True
    assert 3 <= qs["state_count"] <= 6
    # probabilities should sum to ~1.0
    total = sum(s["probability"] for s in qs["states"])
    assert abs(total - 1.0) < 0.01

def test_all_realms_valid():
    qs = ws.superpose()
    for s in qs["states"]:
        assert s["realm"] in ws.REALMS

def test_collapse_returns_real_state():
    ws.superpose()
    r = ws.collapse()
    assert r["collapsed"] is True
    assert r["realized_realm"] in ws.REALMS

def test_collapse_specific_state():
    qs = ws.superpose()
    sid = qs["states"][0]["state_id"]
    r = ws.collapse(sid)
    assert r["collapsed"] is True
    assert r["state_id"] == sid

def test_status_reflects_state():
    ws.superpose()
    st = ws.handler({"action": "status"})
    assert st["superposed"] is True
    assert st["uncollapsed"] is True

def test_status_after_collapse():
    ws.superpose()
    ws.collapse()
    st = ws.handler({"action": "status"})
    assert st["superposed"] is False
    assert st["uncollapsed"] is False
    assert st["chosen_state"] is not None

def test_coherence():
    v = ws.coherence_vitals()
    assert v["wave"] == 425
    assert v["status"] == "active"

def test_persists():
    ws.superpose()
    p = Path(__file__).parent.parent / "data" / "wave425_superposition.json"
    assert p.exists()
    d = json.loads(p.read_text())
    assert "states" in d

def test_action_routing():
    r = ws.handler({"action": "bogus"})
    assert "error" in r
    assert "valid" in r
