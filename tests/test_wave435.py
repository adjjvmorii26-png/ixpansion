"""Tests for Wave 435: Resonance Cartography."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave435_resonance_cartography as m
def test_vitals():
    v = m.coherence_vitals(); assert v["wave"] == 435 and v["ok"] is True
def test_survey():
    r = m.handler({"action": "survey", "modules": ["alpha", "beta", "alpha_lab", "gamma"]})
    assert r["status"] == "surveyed" and "nodes" in r and "edges" in r
def test_atlas_and_status():
    m.handler({"action": "survey", "modules": ["a", "b", "c"]})
    assert m.handler({"action": "atlas"})["status"] == "atlas"
    assert m.handler({"action": "status"})["status"] == "active"
def test_resonates():
    assert "wave431_homestead" in m.resonates_with()
