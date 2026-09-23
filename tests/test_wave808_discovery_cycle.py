"""Wave 808 discovery_cycle_engine tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave808_discovery_cycle_engine as w


def test_diagram_and_advance():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":808,"name":"discovery_cycle_engine","stage":"observe","cycles":0,"promotions":0,"log":[],"status":"test"}'
    )
    d = w.handler({"action": "diagram"})
    assert d["diagram"][0] == "OBSERVE"
    assert "PROMOTE" in d["diagram"][-1]
    a = w.handler({"action": "advance", "note": "signal"})
    assert a["from"] == "observe" and a["to"] == "discover"
    assert a["audio"] is False


def test_review_and_cycle():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":808,"name":"discovery_cycle_engine","stage":"record","cycles":0,"promotions":0,"log":[],"status":"test"}'
    )
    w.handler({"action": "advance"})
    r = w.handler({"action": "review", "decision": "approve"})
    assert r["status"] == "review_approved"
    p = w.handler({"action": "advance"})
    assert p["to"] == "observe"
    assert p["status"] == "cycled"
    assert w.handler({"action": "status"})["cycles"] >= 1
