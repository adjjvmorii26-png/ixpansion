"""Tests for Wave 436: Entropic Weather."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave436_entropic_weather as m
def test_vitals():
    assert m.coherence_vitals()["wave"] == 436
def test_tick():
    r = m.handler({"action": "tick"})
    assert r["status"] == "ticked" and r["sky"] in ("clear", "fog", "storm", "aurora", "drought")
