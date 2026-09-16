"""Experimental waves 743–746."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave743_causal_scar_graph as w743
import wave744_phase_lock_clock as w744
import wave745_mirror_world_delta as w745
import wave746_entropy_weather_front as w746


def test_743_scar():
    r = w743.handler({"action": "scar", "from": "a", "to": "b", "kind": "fail"})
    assert r["status"] == "scarred"
    assert "b" in w743.handler({"action": "paths", "from": "a"})["hop1"]


def test_744_phase_lock():
    for i, ph in enumerate([0.5, 0.52, 0.51]):
        w744.handler({"action": "tick", "node": f"n{i}", "phase": ph})
    assert w744.handler({"action": "lock"})["status"] == "locked"


def test_745_mirror():
    w745.handler({"action": "commit", "key": "x", "value": 1})
    w745.handler({"action": "mirror", "key": "x", "value": 2})
    assert w745.handler({"action": "delta"})["n"] >= 1


def test_746_weather():
    for v in [0.1, 0.12, 0.11]:
        w746.handler({"action": "sample", "v": v})
    assert w746.handler({"action": "forecast"})["front"] in ("calm", "breeze", "storm", "inversion")
