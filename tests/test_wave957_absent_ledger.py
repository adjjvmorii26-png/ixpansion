"""Wave 957 absent_ledger tests. Lab gate only."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave957_absent_ledger as w


def test_absent_ledger():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":957,"name":"absent_ledger","compressions":0,"digest":"","status":"test"}'
    )
    r = w.handler({"action": "compress"})
    assert r["status"] == "compressed"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert r["digest"] == w.absence_digest()
    assert r["width"] == 13
    v = w.coherence_vitals()
    assert v["wave"] == 957
    assert v["ok"] is True
    assert v["organs"] == 5
    links = w.resonates_with()
    assert "wave671_harmony_braid" in links
    assert "wave675_consensus_bloom" in links
    rows = w.absence_rows()
    by_wave = {row["wave"]: row["absent"] for row in rows}
    assert "debt" in by_wave[671]
    assert "quorum" in by_wave[675]
    assert by_wave[674] == ("cycle", "dawns", "rhythm")
    cap = w.handler({"action": "caption"})
    assert cap["audio"] is False
    assert "absence" in cap["caption"]
