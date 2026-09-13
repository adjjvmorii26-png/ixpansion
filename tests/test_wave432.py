"""Tests for Wave 432: Mycelial Index."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave432_mycelial_index as m
def test_vitals():
    v = m.coherence_vitals(); assert v["wave"] == 432 and v["ok"] is True
def test_status():
    r = m.handler({"action": "status"}); assert r["status"] == "active" and r["wave"] == 432
def test_seed_and_query():
    r = m.handler({"action": "seed", "key": "tide", "note": "tide follows proof density"})
    assert r["status"] == "seeded"
    q = m.handler({"action": "query", "key": "tide"})
    assert q["status"] == "query"
def test_resonates():
    assert "wave431_homestead" in m.resonates_with()
