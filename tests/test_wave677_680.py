"""Waves 677–680 post-Council innovations."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave677_void_meter as w677
import wave678_braid_debt_oracle as w678
import wave679_bloom_cascade as w679
import wave680_dual_track_sentinel as w680

def test_677_void_meter():
    assert w677.coherence_vitals()["wave"] == 677
    r = w677.handler({"action": "record", "kind": "silence", "amount": 2.0, "label": "skipped_audio"})
    assert r["status"] == "recorded" and r["void_capital"] >= 2.0
    assert w677.handler({"action": "spend", "amount": 1.0})["status"] == "spent"

def test_678_braid_debt_oracle():
    assert w678.coherence_vitals()["wave"] == 678
    w678.handler({"action": "observe", "debt": 0.5})
    w678.handler({"action": "observe", "debt": 1.2})
    r = w678.handler({"action": "observe", "debt": 1.8})
    assert r["status"] == "observed"

def test_679_bloom_cascade():
    assert w679.coherence_vitals()["wave"] == 679
    root = w679.handler({"action": "root", "name": "horizon_cap"})
    assert root["status"] == "rooted"
    b = w679.handler({"action": "branch", "parent": root["id"], "name": "child_cap"})
    assert b["status"] == "branched" and b["depth"] == 1

def test_680_dual_track_sentinel():
    assert w680.coherence_vitals()["wave"] == 680
    r = w680.handler({
        "action": "scan",
        "paths": ["lab/ops/x.py", "api/wave676_scar_compass.py", "api/aleph_bot.py"],
    })
    assert r["status"] == "scanned"
    assert r["lab_hits"] >= 1 and r["aleph_hits"] >= 1
