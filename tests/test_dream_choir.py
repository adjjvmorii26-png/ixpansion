"""Dream Choir on main — wave710 module + wave709 ritual actions."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))

import wave710_dream_choir as w710
import wave709_rift_choir_twin_d28a as w709


def test_710():
    v = w710.coherence_vitals()
    assert v["wave"] == 710
    assert v["ok"] is True


def test_710_sing_action():
    r = w710.handler({"action": "sing", "voices": 2})
    assert r["module"] == "wave710_dream_choir"
    assert r["ok"] is True


def test_709_awaken():
    assert w709.coherence_vitals()["wave"] == 709
    r = w709.handler({"action": "awaken"})
    assert r["status"] == "awakened"


def test_709_rift():
    r = w709.handler({"action": "rift", "gap": 0.2})
    assert r["rift"] >= 0.2


def test_709_hear():
    r = w709.handler({"action": "hear", "voice": "rift_choir_twin"})
    assert r["choir_n"] >= 1
