"""Waves 683-686 post-Council innovations."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave683_void_meter as w683
import wave684_braid_debt_oracle as w684
import wave685_bloom_cascade as w685
import wave686_dual_track_sentinel as w686


def test_683_void_meter():
    cv = w683.coherence_vitals()
    assert cv["wave"] == 683 and cv["module"] == "wave683_void_meter"
    r = w683.handler({"action": "record", "kind": "silence", "amount": 2.0, "label": "skipped_audio"})
    assert r["status"] == "recorded" and r["void_capital"] >= 2.0
    assert w683.handler({"action": "spend", "amount": 1.0})["status"] == "spent"
    st = w683.handler({"action": "status"})
    assert st["void_capital"] >= 1.0


def test_684_braid_debt_oracle():
    cv = w684.coherence_vitals()
    assert cv["wave"] == 684 and cv["module"] == "wave684_braid_debt_oracle"
    w684.handler({"action": "observe", "debt": 0.5})
    w684.handler({"action": "observe", "debt": 1.2})
    r = w684.handler({"action": "observe", "debt": 1.8})
    assert r["status"] == "observed"
    st = w684.handler({"action": "status"})
    assert st["samples"] >= 3


def test_685_bloom_cascade():
    cv = w685.coherence_vitals()
    assert cv["wave"] == 685 and cv["module"] == "wave685_bloom_cascade"
    root = w685.handler({"action": "root", "name": "horizon_cap"})
    assert root["status"] == "rooted"
    b = w685.handler({"action": "branch", "parent": root["id"], "name": "child_cap"})
    assert b["status"] == "branched" and b["depth"] == 1
    tree = w685.handler({"action": "tree"})
    assert tree["nodes"] >= 2


def test_686_dual_track_sentinel():
    cv = w686.coherence_vitals()
    assert cv["wave"] == 686 and cv["module"] == "wave686_dual_track_sentinel"
    r = w686.handler({
        "action": "scan",
        "paths": ["lab/ops/x.py", "api/wave676_scar_compass.py", "api/aleph_bot.py"],
    })
    assert r["status"] == "scanned"
    assert r["lab_hits"] >= 1 and r["aleph_hits"] >= 1
    adv = w686.handler({"action": "advisories"})
    assert adv["wave"] == 686
