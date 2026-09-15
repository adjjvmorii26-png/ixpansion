"""Velocity family: momentum, inertia, terminal, jerk."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave690_momentum_braid as w690
import wave691_inertia_ledger as w691
import wave692_terminal_velocity as w692
import wave693_jerk_sensor as w693

def test_690_momentum():
    assert w690.coherence_vitals()["wave"] == 690
    r = w690.handler({"action": "tick", "lab_v": 3.0, "aleph_v": 2.5})
    assert r["status"] == "ticked" and r["momentum"] > 0

def test_691_inertia():
    assert w691.coherence_vitals()["wave"] == 691
    w691.handler({"action": "weigh", "module": "harmony_braid", "mass": 2.0})
    r = w691.handler({"action": "lighten", "module": "harmony_braid", "delta": 0.5})
    assert r["status"] == "lightened" and r["mass"] == 1.5

def test_692_terminal():
    assert w692.coherence_vitals()["wave"] == 692
    w692.handler({"action": "set_terminal", "terminal": 4.0})
    r = w692.handler({"action": "observe", "v": 5.0})
    assert r["status"] == "observed" and r["coasting"] is True

def test_693_jerk():
    assert w693.coherence_vitals()["wave"] == 693
    w693.handler({"action": "sample", "v": 1.0})
    w693.handler({"action": "sample", "v": 2.0})
    r = w693.handler({"action": "sample", "v": 5.0})
    assert r["status"] == "sampled"
