"""Wave 770 copilot_council_pulse — lab-gated organ tests."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
sys.path.insert(0, str(Path(__file__).parent.parent))

import wave770_copilot_council_pulse as w770


def setup_function(_fn=None):
    w770.DATA.mkdir(parents=True, exist_ok=True)
    w770.STATE_FILE.write_text(json.dumps({
        "wave": 770, "name": "copilot_council_pulse",
        "pulses": 0, "last_posture": "unknown",
        "last_headline": "", "last_ts": None, "status": "test",
    }))


def test_contract():
    v = w770.coherence_vitals()
    assert v["wave"] == 770
    assert v["name"] == "copilot_council_pulse"
    assert "wave769_void_index" in w770.resonates_with()
    assert callable(w770.handler)


def test_pulse_and_caption():
    setup_function()
    r = w770.handler({"action": "pulse"})
    assert r["status"] == "pulsed"
    assert r["payload"] is None
    assert r["audio"] is False
    assert r["surface"] == "silence"
    assert r["posture"] in ("green", "amber", "red", "unknown")
    cap = w770.handler({"action": "caption"})
    assert cap["audio"] is False
    assert "council" in cap["caption"]
    st = w770.handler({"action": "status"})
    assert st["pulses"] >= 1
