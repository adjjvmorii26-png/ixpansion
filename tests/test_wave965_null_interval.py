"""Wave 965 null_interval tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave965_null_interval as w


def test_null_interval():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "gap", "length": 42})
    assert r["status"] == "gapped"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert r["length"] == 42
    assert len(r["token"]) == 10
    assert r["gaps"] == 1
    short = w.handler({"action": "gap", "length": 0})
    assert short["length"] == 0
    assert short["gaps"] == 2
    v = w.coherence_vitals()
    assert v["wave"] == 965
    assert v["ok"] is True
    assert "wave964_still_point" in w.resonates_with()
    assert "wave950_hush_margin" in w.resonates_with()
