"""Wave 977 entropy_hush tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave977_entropy_hush as w


def test_compress():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "compress", "entropy": 0.37, "seed": "pulse"})
    assert r["status"] == "hushed"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert len(r["token"]) == 10
    assert r["compressions"] == 1
    r2 = w.handler({"action": "compress", "entropy": 0.37, "seed": "pulse"})
    assert r2["token"] == r["token"]
    assert r2["compressions"] == 2
    v = w.coherence_vitals()
    assert v["wave"] == 977
    assert v["ok"] is True
    assert "wave949_council_witness" in w.resonates_with()
    assert "wave671_harmony_braid" in w.resonates_with()
