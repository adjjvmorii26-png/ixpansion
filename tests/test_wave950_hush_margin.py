"""Wave 950 hush_margin tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave950_hush_margin as w


def test_hush_margin():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "margin", "token": "abcdef123456"})
    assert r["status"] == "margined"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert r["token_width"] == 12
    assert r["margin"] == 1
    short = w.handler({"action": "margin", "token": "abc"})
    assert short["margin"] == 9
    assert short["margins"] == 2
    v = w.coherence_vitals()
    assert v["wave"] == 950
    assert v["ok"] is True
    assert "wave949_council_witness" in w.resonates_with()
    assert "wave681_hush_membrane" in w.resonates_with()
