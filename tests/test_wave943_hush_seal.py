"""Wave 943 hush_seal tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave943_hush_seal as w


def test_seal():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":943,"name":"hush_seal","seal":"","source_n":0,"status":"test"}'
    )
    r = w.handler({"action": "seal", "tokens": ["abcd1234efgh5678", "zzzz1111yyyy2222"]})
    assert r["status"] == "sealed"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert len(r["seal"]) == 16
    assert r["source_n"] == 2


def test_vitals_and_resonance():
    v = w.coherence_vitals()
    assert v["wave"] == 943
    assert v["ok"] is True
    assert "wave942_hush_ledger" in w.resonates_with()
