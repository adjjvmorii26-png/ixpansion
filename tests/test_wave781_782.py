"""Waves 781–782 tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave781_chrono_scar_clock as w781
import wave782_dream_share_bus as w782


def test_781_open_close():
    w781.DATA.mkdir(parents=True, exist_ok=True)
    w781.STATE_FILE.write_text(
        '{"wave":781,"name":"chrono_scar_clock","scars":[],"ticks":0,"status":"test"}'
    )
    assert w781.coherence_vitals()["wave"] == 781
    o = w781.handler({"action": "open", "label": "t", "budget_ms": 5000})
    assert o["status"] == "opened"
    assert o["audio"] is False
    c = w781.handler({"action": "close", "id": o["scar"]["id"]})
    assert c["status"] == "closed"
    assert c["within_budget"] is True


def test_782_share():
    w782.DATA.mkdir(parents=True, exist_ok=True)
    w782.STATE_FILE.write_text(
        '{"wave":782,"name":"dream_share_bus","dreams":0,"status":"test"}'
    )
    r = w782.handler({"action": "share", "topic": "lab"})
    assert r["status"] == "shared"
    assert r["packet"]["audio"] is False
    assert len(r["packet"]["lines"]) >= 1
