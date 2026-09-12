"""Tests for Waves 416-417."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave416_paradox_singularity as wp
import wave417_causality_loop as wc

# Wave 416 tests
def test_detect():
    s = wp.detect_singularity()
    assert s["module"] == "wave416_paradox_singularity"
    assert "singularity_level" in s
    assert s["singularity_state"] in ("approaching", "critical")

def test_resolve():
    s = wp.resolve_singularity()
    assert s["resolution_status"] in ("resolved", "ongoing")

def test_status():
    st = wp.handler({"action": "status"})
    assert "singularity_level" in st
    assert "state" in st
    assert "power" in st

# Wave 417 tests
def test_build():
    c = wc.build_causality_chain()
    assert c["module"] == "wave417_causality_loop"
    assert len(c["causality_chains"]) >= 3
    assert "total_loops" in c

def test_chains():
    r = wc.handler({"action": "chains"})
    assert "chains" in r
    assert "total" in r

def test_stability():
    s = wc.handler({"action": "stability"})
    assert "stability" in s
    assert "integrity" in s
    assert "loops" in s

def test_coherence_416():
    v = wp.coherence_vitals()
    assert v["wave"] == 416

def test_coherence_417():
    v = wc.coherence_vitals()
    assert v["wave"] == 417

def test_416_persists():
    wp.detect_singularity()
    p = Path(__file__).parent.parent / "data" / "wave416_paradox_singularity.json"
    assert p.exists()
    d = json.loads(p.read_text())
    assert "singularity_level" in d

def test_417_persists():
    wc.build_causality_chain()
    p = Path(__file__).parent.parent / "data" / "wave417_causality_loop.json"
    assert p.exists()
    d = json.loads(p.read_text())
    assert "causality_chains" in d
