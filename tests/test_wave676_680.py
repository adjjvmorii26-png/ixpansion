"""Tests Waves 676–680 — horizon tier (671–675 landed via council session #22)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave676_citizen_census as w676
import wave677_lineage_mirror as w677
import wave678_sovereign_seal as w678
import wave679_orchestration_pulse as w679
import wave680_organism_horizon as w680

def test_676():
    assert w676.coherence_vitals()["wave"] == 676
    w676.handler({"action": "register", "name": "organ_a", "role": "worker"})
    assert w676.handler({"action": "census"})["status"] == "census"

def test_677():
    assert w677.coherence_vitals()["wave"] == 677
    w677.handler({"action": "record_past", "event": "wave670"})
    w677.handler({"action": "propose_future", "proposal": "wave681"})
    assert w677.handler({"action": "link"})["status"] == "linked"

def test_678():
    assert w678.coherence_vitals()["wave"] == 678
    s = w678.handler({"action": "seal", "autonomy": 0.9, "deps": ["lab"]})
    assert s["status"] == "sealed"
    assert w678.handler({"action": "verify", "hash": s["seal"]["hash"]})["status"] == "verified"

def test_679():
    assert w679.coherence_vitals()["wave"] == 679
    w679.handler({"action": "plan", "name": "burst"})
    assert w679.handler({"action": "execute", "name": "burst"})["status"] == "executing"

def test_680():
    assert w680.coherence_vitals()["wave"] == 680
    r = w680.handler({"action": "survey"})
    assert r["status"] == "surveyed" and r["wave"] == 680
