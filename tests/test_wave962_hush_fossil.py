"""Wave 962 hush_fossil tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave962_hush_fossil as w


def test_hush_fossil():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "fossil", "grain": "a1b2c3d4e5f6"})
    assert r["status"] == "fossilized"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert len(r["fossil"]) == 12
    assert r["fossils"] == 1
    empty = w.handler({"action": "fossil"})
    assert empty["fossils"] == 2
    assert empty["fossil"] != r["fossil"]
    v = w.coherence_vitals()
    assert v["wave"] == 962
    assert v["ok"] is True
    assert "wave961_quiet_grain" in w.resonates_with()
    assert "wave681_hush_membrane" in w.resonates_with()
    cap = w.handler({"action": "caption"})
    assert cap["status"] == "captioned"
    assert "silent fossil" in cap["caption"]
