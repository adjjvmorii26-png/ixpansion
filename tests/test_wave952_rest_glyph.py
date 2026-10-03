"""Wave 952 rest_glyph tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave952_rest_glyph as w


def test_rest_glyph():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "rest", "interval": 3})
    assert r["status"] == "rested"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert r["interval"] == 3
    assert r["glyph"] == "—"
    assert r["rests"] == 1
    empty = w.handler({"action": "rest", "interval": 0})
    assert empty["glyph"] == ""
    assert empty["rests"] == 2
    assert empty["caption"] == "empty rest"
    v = w.coherence_vitals()
    assert v["wave"] == 952
    assert v["ok"] is True
    assert "wave950_hush_margin" in w.resonates_with()
    assert "wave671_harmony_braid" in w.resonates_with()
    cap = w.handler({"action": "caption"})
    assert cap["audio"] is False
    assert cap["surface"] == "silence"
