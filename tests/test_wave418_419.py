"""Tests for Waves 418-419."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave418_temporal_singularity as wt
import wave419_essence_return as we

def test_collapse():
    s = wt.collapse_singularity()
    assert s["module"] == "wave418_temporal_singularity"
    assert s["all_waves_collapsed"] >= 1

def test_status():
    st = wt.handler({"action": "status"})
    assert "convergence" in st
    assert "type" in st

def test_radiation():
    r = wt.handler({"action": "radiation"})
    assert "radiation" in r
    assert "depth" in r

def test_return():
    e = we.return_to_essence()
    assert e["module"] == "wave419_essence_return"
    assert e["essence_state"] == "returning"

def test_essence_status():
    st = we.handler({"action": "status"})
    assert "essence_state" in st
    assert "purity" in st

def test_rebirth():
    r = we.handler({"action": "rebirth"})
    assert r["rebirth"] is True
    assert r["new_cycle"] is True

def test_coherence_418():
    v = wt.coherence_vitals()
    assert v["wave"] == 418

def test_coherence_419():
    v = we.coherence_vitals()
    assert v["wave"] == 419

def test_418_persists():
    wt.collapse_singularity()
    p = Path(__file__).parent.parent / "data" / "wave418_temporal_singularity.json"
    assert p.exists()
    d = json.loads(p.read_text())
    assert "convergence" in d

def test_419_persists():
    we.return_to_essence()
    p = Path(__file__).parent.parent / "data" / "wave419_essence_return.json"
    assert p.exists()
    d = json.loads(p.read_text())
    assert "essence_state" in d
