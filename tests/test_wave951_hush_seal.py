"""Wave 951 hush_seal tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave951_hush_seal as w


def test_hush_seal():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "seal", "token": "abcdef123456", "margin": 1})
    assert r["status"] == "sealed"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert len(r["digest"]) == 12
    assert r["seals"] == 1
    r2 = w.handler({"action": "seal", "token": "xyz", "margin": 9})
    assert r2["seals"] == 2
    v = w.coherence_vitals()
    assert v["wave"] == 951
    assert v["ok"] is True
    assert "wave950_hush_margin" in w.resonates_with()
    assert "wave949_council_witness" in w.resonates_with()
