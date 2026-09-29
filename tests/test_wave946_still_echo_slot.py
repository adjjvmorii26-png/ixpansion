"""Wave 946 still_echo_slot tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave946_still_echo_slot as w


def test_echo_slot():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":946,"name":"still_echo_slot","echoes":0,"slots":["","","","","","","",""],"head":0,"status":"test"}'
    )
    r = w.handler({"action": "echo", "residue": "abcd1234"})
    assert r["status"] == "echoed"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["residue"] == "abcd1234"
    assert r["surface"] == "silence"
    v = w.coherence_vitals()
    assert v["wave"] == 946
    assert v["ok"] is True
    assert "wave944_hush_still" in w.resonates_with()
