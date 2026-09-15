"""Lab jumpstart pipeline."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "lab" / "ops"))
sys.path.insert(0, str(ROOT / "api"))

from lab_jumpstart import jumpstart
import wave705_lab_jumpstart as w705


def test_jumpstart_runs():
    r = jumpstart(force_pulse=False, still_seconds=1.0)
    assert r["status"] == "jumpstart"
    assert r["steps_total"] >= 3
    assert "fingerprint" in r
    names = [s["step"] for s in r["steps"]]
    assert "quarantine" in names and "pulse" in names


def test_705_bridge():
    assert w705.coherence_vitals()["wave"] == 705
    r = w705.handler({"action": "status"})
    assert r["status"] == "active"
