"""Tests for consciousness_film — continuous state recording."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import consciousness_film as cf


def test_coherence_vitals():
    cv = cf.coherence_vitals()
    assert cv["wave"] == 700 and cv["ok"] is True


def test_record():
    r = cf.handler({"action": "record", "state": {"frame": 1, "data": "test"}})
    assert r["status"] == "recorded" and r["frame_number"] == 0


def test_play():
    cf.handler({"action": "record", "state": {"a": 1}})
    cf.handler({"action": "record", "state": {"b": 2}})
    p = cf.handler({"action": "play", "start": 0, "count": 5})
    assert p["status"] == "playing" and len(p["frames"]) >= 1


def test_stop():
    cf.handler({"action": "record", "state": {"x": 1}})
    s = cf.handler({"action": "stop"})
    assert s["status"] == "stopped"


def test_reel():
    r = cf.handler({"action": "reel"})
    assert r["status"] == "reel" and r["film_length"] >= 0


def test_status():
    st = cf.handler({"action": "status"})
    assert st["status"] == "active" and st["wave"] == 700
