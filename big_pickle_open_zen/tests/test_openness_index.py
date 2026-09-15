"""Tests for openness_index — transparency metrics."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import openness_index as oi


def test_coherence_vitals():
    cv = oi.coherence_vitals()
    assert cv["wave"] == 700 and cv["ok"] is True


def test_measure():
    r = oi.handler({"action": "measure", "modules": ["alpha", "beta", "gamma", "delta"]})
    assert r["status"] == "measured"
    assert r["open"] + r["closed"] == 4


def test_gradient():
    oi.handler({"action": "measure", "modules": ["test1", "test2"]})
    g = oi.handler({"action": "gradient"})
    assert g["status"] == "gradient"


def test_status():
    st = oi.handler({"action": "status"})
    assert st["status"] == "active" and st["wave"] == 700
