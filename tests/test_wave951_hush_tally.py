"""Wave 951 hush_tally tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave951_hush_tally as w


def test_hush_tally():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "tally", "margin": 1})
    assert r["status"] == "tallied"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert r["margin"] == 1
    assert r["tallies"] == 1
    again = w.handler({"action": "tally", "margin": -3})
    assert again["margin"] == 0
    assert again["tallies"] == 2
    cap = w.handler({"action": "caption"})
    assert cap["caption"] == "silent tallies 2"
    assert cap["audio"] is False
    v = w.coherence_vitals()
    assert v["wave"] == 951
    assert v["ok"] is True
    assert "wave950_hush_margin" in w.resonates_with()
    assert "wave681_hush_membrane" in w.resonates_with()
