"""Wave 944 hush_still tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave944_hush_still as w


def test_still():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":944,"name":"hush_still","still":"","source":"","status":"test"}'
    )
    r = w.handler({"action": "still", "token": "abcd1234efgh5678"})
    assert r["status"] == "stilled"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert len(r["still"]) == 8
    assert r["still"] == w._still_of("abcd1234efgh5678")


def test_vitals_and_resonance():
    v = w.coherence_vitals()
    assert v["wave"] == 944
    assert v["ok"] is True
    assert "wave942_hush_ledger" in w.resonates_with()
