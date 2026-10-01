"""Wave 949 council_witness tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave949_council_witness as w


def test_witness():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "witness"})
    assert r["status"] == "witnessed"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert len(r["token"]) == 12
    r2 = w.handler({"action": "witness"})
    assert r2["token"] == r["token"]
    assert r2["witnesses"] == 2
    v = w.coherence_vitals()
    assert v["wave"] == 949
    assert v["ok"] is True
    assert v["organs"] == 5
    assert "wave671_harmony_braid" in w.resonates_with()
    assert "wave675_consensus_bloom" in w.resonates_with()
