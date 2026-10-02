"""Wave 951 seam_index tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave951_seam_index as w


def test_index():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "index"})
    assert r["status"] == "indexed"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert len(r["joins"]) == 4
    assert r["joins"][0]["join"] == "harmony_braid|root_archive"
    assert r["joins"][-1]["join"] == "dawn_ledger|consensus_bloom"
    assert all(len(j["digest"]) == 8 for j in r["joins"])
    r2 = w.handler({"action": "index"})
    assert r2["joins"] == r["joins"]
    assert r2["indexes"] == 2
    v = w.coherence_vitals()
    assert v["wave"] == 951
    assert v["ok"] is True
    assert v["seams"] == 4
    assert "wave671_harmony_braid" in w.resonates_with()
    assert "wave949_council_witness" in w.resonates_with()
    cap = w.handler({"action": "caption"})
    assert cap["audio"] is False
    assert "seams" in cap["caption"]
