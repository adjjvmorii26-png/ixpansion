"""Wave 947 echo_fold tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave947_echo_fold as w


def test_echo_fold():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":947,"name":"echo_fold","folds":0,"digest":"","status":"test"}'
    )
    r = w.handler({"action": "fold", "slots": ["abcd", "ef01"]})
    assert r["status"] == "folded"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert r["digest"]
    assert r["digest"] != "empty"
    v = w.coherence_vitals()
    assert v["wave"] == 947
    assert v["ok"] is True
    assert "wave946_still_echo_slot" in w.resonates_with()
