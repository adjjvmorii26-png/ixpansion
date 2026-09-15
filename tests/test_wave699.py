"""Wave 699 Entropy Heatmap tests."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave699_entropy_heatmap as w


def test_coherence_vitals():
    cv = w.coherence_vitals()
    assert cv["wave"] == 699 and cv["ok"] is True


def test_update():
    mods = ["module_a", "module_b", "module_c"]
    r = w.handler({"action": "update", "modules": mods, "grid_size": 8})
    assert r["status"] == "updated" and r["modules"] == 3
    st = w.handler({"action": "status"})
    assert st["total_modules"] == 3 and st["entropy_average"] >= 0.0


def test_hot_zones():
    w.handler({"action": "update", "modules": ["hot_mod", "cold_mod"], "grid_size": 8})
    hz = w.handler({"action": "hot_zones"})
    assert hz["status"] == "hot_zones"
    cz = w.handler({"action": "cold_zones"})
    assert cz["status"] == "cold_zones"


def test_cell():
    w.handler({"action": "update", "modules": ["test_mod"], "grid_size": 10})
    c = w.handler({"action": "cell", "row": 0, "col": 0})
    assert c["status"] == "cells"


def test_status():
    st = w.handler({"action": "status"})
    assert st["status"] == "active" and st["wave"] == 699
