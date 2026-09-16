"""Ouroboros infinite leap."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "lab" / "ops"))
sys.path.insert(0, str(ROOT / "api"))

from lab.ops.ouroboros import dream_name, run, cycle
import api.wave708_ouroboros as w708


def test_dream_name_deterministic():
    a, ma = dream_name("aabbccddeeff001122")
    b, mb = dream_name("aabbccddeeff001122")
    assert a == b and ma["name"] == mb["name"]
    c, _ = dream_name("ffffffffffff000000")
    assert c != a


def test_cycle_dream_only():
    r = cycle(scaffold=False, dream_only=True)
    assert r["ok"] and "dream" in r
    assert r["dream"]["slug"]


def test_run_once():
    m = run(cycles=1, scaffold=False, dream_only=True)
    assert m["status"] == "ouroboros" and m["leap"] == "infinite"


def test_708():
    assert w708.coherence_vitals()["wave"] == 708
