"""Dream choir + awakened void twin."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "lab" / "ops"))
sys.path.insert(0, str(ROOT / "api"))

from dream_choir import sing
import wave710_dream_choir as w710
import wave709_rift_choir_twin_d28a as w709


def test_sing():
    m = sing(voices=3)
    assert m["ok"] and m["voices"] == 3
    assert "resonance" in m


def test_710():
    assert w710.coherence_vitals()["wave"] == 710


def test_709_awaken_and_rift():
    assert w709.coherence_vitals()["wave"] == 709
    r = w709.handler({"action": "awaken"})
    assert r["status"] == "awakened"
    r2 = w709.handler({"action": "rift", "gap": 0.2})
    assert r2["rift"] >= 0.2
    r3 = w709.handler({"action": "hear", "voice": "rift_choir_twin"})
    assert r3["choir_n"] >= 1
