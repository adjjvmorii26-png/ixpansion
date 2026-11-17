"""Wave 951 hush_compressor tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave951_hush_compressor as w


def test_hush_compressor():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "compress", "residual": "session residue to fold"})
    assert r["status"] == "compressed"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert r["ratio"] < 1.0
    assert r["before"] > 0
    v = w.coherence_vitals()
    assert v["wave"] == 951
    assert v["ok"] is True
    assert v["compressions"] == 1
    assert "wave950_hush_margin" in w.resonates_with()
    cap = w.handler({"action": "caption"})
    assert cap["status"] == "captioned"
    assert "silence" in cap["caption"]
