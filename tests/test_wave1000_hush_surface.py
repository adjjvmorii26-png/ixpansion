"""Minimal test for Wave 1000 Hush Surface."""
import importlib.util
from pathlib import Path

def load_wave():
    p = Path(__file__).parent.parent / "api" / "wave1000_hush_surface.py"
    spec = importlib.util.spec_from_file_location("wave1000", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_vitals_and_contract():
    w = load_wave()
    v = w.coherence_vitals()
    assert v["wave"] == 1000
    assert v["ok"] is True
    assert "wave671_harmony_braid" in w.resonates_with()

def test_surface_and_compress():
    w = load_wave()
    r = w.handler({"action": "surface", "note": "lab pulse", "depth": 0.5})
    assert r["status"] == "surfaced"
    assert r["silence_depth"] > 0
    c = w.handler({"action": "compress"})
    assert c["status"] == "compressed"
    assert c["compressions"] >= 1
    assert c["surfaces"] == 0
