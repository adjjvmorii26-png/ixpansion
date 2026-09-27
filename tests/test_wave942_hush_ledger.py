"""Wave 942 hush_ledger tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave942_hush_ledger as w


def test_record():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":942,"name":"hush_ledger","entries":[],"status":"test"}'
    )
    r = w.handler({"action": "record", "token": "abcd1234efgh5678"})
    assert r["status"] == "recorded"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert r["token"] == "abcd1234efgh5678"


def test_vitals_and_resonance():
    v = w.coherence_vitals()
    assert v["wave"] == 942
    assert v["ok"] is True
    assert "wave941_hush_fold" in w.resonates_with()
