"""Wave 951 still_seam tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave951_still_seam as w


def test_still_seam():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "seam", "residual": "quiet residue"})
    assert r["status"] == "seamed"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert r["charge"] == 13
    assert r["seams"] == 1
    empty = w.handler({"action": "seam", "residual": ""})
    assert empty["charge"] == 0
    assert empty["seams"] == 2
    v = w.coherence_vitals()
    assert v["wave"] == 951
    assert v["ok"] is True
    assert "wave950_hush_margin" in w.resonates_with()
    assert "wave949_council_witness" in w.resonates_with()
