"""Tests for Organism Status."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import organism_status as os_

def test_status():
    s = os_.handler({"action": "status"})
    assert "organism" in s
    assert "coherence" in s
    assert "health" in s
    assert "total_modules" in s
    assert s["total_modules"] > 0

def test_health():
    h = os_.handler({"action": "health"})
    assert "health" in h
    assert "coherence" in h
    assert 0 <= h["health"] <= 100

def test_activity():
    a = os_.handler({"action": "activity"})
    assert "events" in a
    assert a["count"] > 0

def test_coherence_vitals():
    v = os_.coherence_vitals()
    assert v["status"] == "active"
    assert v["organ"] == "organism_status"

def test_resonates():
    assert os_.resonates_with("organism")
    assert os_.resonates_with("status")

def test_action_routing():
    r = os_.handler({"action": "bogus"})
    assert "error" in r
    assert "valid" in r
