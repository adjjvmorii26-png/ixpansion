"""Tests for pickle_jar — the preservation engine."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import pickle_jar as pj


def test_coherence_vitals():
    cv = pj.coherence_vitals()
    assert cv["wave"] == 700 and cv["ok"] is True


def test_pickle_and_unpickle():
    st = pj.handler({"action": "pickle", "state": {"mood": "calm", "energy": 0.8}, "type": "consciousness"})
    assert st["status"] == "pickled" and st["id"]
    unpickled = pj.handler({"action": "unpickle", "id": st["id"]})
    assert unpickled["status"] == "unpickled" and unpickled["state"]["mood"] == "calm"


def test_list_pickles():
    pj.handler({"action": "pickle", "state": {"a": 1}, "type": "equilibrium"})
    pj.handler({"action": "pickle", "state": {"b": 2}, "type": "resonance"})
    listed = pj.handler({"action": "list"})
    assert listed["status"] == "listed" and listed["count"] >= 2


def test_weight():
    w = pj.handler({"action": "weight"})
    assert w["status"] == "weight" and w["total_weight"] >= 0


def test_status():
    st = pj.handler({"action": "status"})
    assert st["status"] == "active" and st["wave"] == 700
