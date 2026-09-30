"""Wave 948 fold_register tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave948_fold_register as w


def test_register():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":948,"name":"fold_register","entries":[],"status":"test"}'
    )
    r = w.handler({"action": "register", "digest": "abc123def4567890"})
    assert r["status"] == "registered"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert r["digest"] == "abc123def4567890"
    assert "abc123def4567890" in r["entries"]
    r2 = w.handler({"action": "register", "digest": "abc123def4567890"})
    assert r2["entries"].count("abc123def4567890") == 1
    v = w.coherence_vitals()
    assert v["wave"] == 948
    assert v["ok"] is True
    assert "wave947_echo_fold" in w.resonates_with()
