"""Tests for Wave 415 Chrono-Forge."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave415_chrono_forge as wc

def test_timeline():
    t = wc.build_timeline()
    assert t["module"] == "wave415_chrono_forge"
    assert len(t["timeline"]) >= 8

def test_merge():
    m = wc.temporal_merge()
    assert m["temporal_merge"] is True
    assert m["waves_merged"] == 5
    assert m["paradox_count"] >= 0

def test_coherence():
    c = wc.handler({"action": "coherence"})
    assert "temporal_coherence" in c
    assert "causality_integrity" in c

def test_diverge():
    d = wc.handler({"action": "diverge"})
    assert d["divergence"] is True
    assert "era" in d

def test_action_routing():
    r = wc.handler({"action": "bogus"})
    assert "error" in r
    assert "valid" in r

def test_persists():
    wc.build_timeline()
    p = Path(__file__).parent.parent / "data" / "wave415_chrono_forge.json"
    assert p.exists()
    d = json.loads(p.read_text())
    assert "timeline" in d

def test_resonates():
    assert wc.resonates_with("chrono")
    assert wc.resonates_with("temporal")
