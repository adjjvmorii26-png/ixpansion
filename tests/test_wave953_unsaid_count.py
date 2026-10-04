"""Wave 953 unsaid_count tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave953_unsaid_count as w


def test_unsaid_count():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "withhold"})
    assert r["status"] == "withheld"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["names"] is None
    assert r["surface"] == "silence"
    assert r["unsaid"] == 5
    assert "harmony_braid" not in str(r)
    partial = w.handler({"action": "withhold", "names": ["naming_well", "dawn_ledger"]})
    assert partial["unsaid"] == 2
    assert partial["withholds"] == 2
    assert partial["names"] is None
    v = w.coherence_vitals()
    assert v["wave"] == 953
    assert v["ok"] is True
    assert "wave949_council_witness" in w.resonates_with()
    assert "wave673_naming_well" in w.resonates_with()
    cap = w.handler({"action": "caption"})
    assert cap["caption"] == "unsaid 2"
    assert cap["audio"] is False
