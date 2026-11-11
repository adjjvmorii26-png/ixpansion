"""Wave 951 silence_ledger tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave951_silence_ledger as w


def test_record_and_vitals():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "record", "gate": "lab-smoke", "ok": True})
    assert r["status"] == "recorded"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert r["aleph_ci"] is False
    assert len(r["token"]) == 12
    assert r["entries"] == 1
    r2 = w.handler({"action": "record", "gate": "lab-graft", "ok": True})
    assert r2["entries"] == 2
    assert r2["token"] != r["token"]
    v = w.coherence_vitals()
    assert v["wave"] == 951
    assert v["ok"] is True
    assert v["surface"] == "silence"
    assert "wave950_hush_margin" in w.resonates_with()
    assert "wave949_council_witness" in w.resonates_with()
    cap = w.handler({"action": "caption"})
    assert "hush" in cap["caption"] or "ledger" in cap["caption"]
    assert cap["audio"] is False
