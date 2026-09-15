"""Burst 456–459."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave456_echo_budget as w456
import wave457_phase_lock as w457
import wave458_soft_fork_garden as w458
import wave459_quiet_crown_auction as w459

def test_456_echo_budget():
    assert w456.coherence_vitals()["wave"] == 456
    r = w456.handler({"action": "echo", "target": "wave450", "cost": 1.0})
    assert r["status"] == "echoed"

def test_457_phase_lock():
    assert w457.coherence_vitals()["wave"] == 457
    w457.handler({"action": "set", "node": "a", "phase": 0.1})
    r = w457.handler({"action": "set", "node": "b", "phase": 0.12})
    assert r["status"] == "set" and r["lock"] >= 0

def test_458_soft_fork():
    assert w458.coherence_vitals()["wave"] == 458
    p = w458.handler({"action": "plant", "name": "exp_lane"})
    assert p["status"] == "planted"
    w458.handler({"action": "nourish", "id": p["id"], "amount": 1.2})
    pr = w458.handler({"action": "promote", "id": p["id"], "threshold": 1.0})
    assert pr["status"] == "promoted"

def test_459_quiet_crown():
    assert w459.coherence_vitals()["wave"] == 459
    w459.handler({"action": "bid", "peer": "node_a", "void": 3.0, "captions": 0})
    w459.handler({"action": "bid", "peer": "node_b", "void": 1.0, "captions": 5})
    c = w459.handler({"action": "close"})
    assert c["status"] == "crowned" and c["crown"]["peer"] == "node_a"
