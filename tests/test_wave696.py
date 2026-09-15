"""Wave 696 Harmonic Resonance Oracle tests."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave696_harmonic_resonance_oracle as w


def test_coherence_vitals():
    cv = w.coherence_vitals()
    assert cv["wave"] == 696 and cv["ok"] is True


def test_resonates_with():
    r = w.resonates_with()
    assert len(r) > 0


def test_scan():
    s = w.handler({"action": "scan", "modules": ["organism_core", "wave694"]})
    assert s["status"] == "scanned" and s["harmony_score"] >= 0.0
    r = w.handler({"action": "resonance", "module": "organism_core"})
    assert r["status"] == "resonance"
    st = w.handler({"action": "status"})
    assert st["total_scan"] == 1


def test_patterns():
    p = w.handler({"action": "patterns"})
    assert p["status"] == "patterns" and len(p["patterns"]) == 1


def test_status():
    st = w.handler({"action": "status"})
    assert st["status"] == "active" and st["wave"] == 696
