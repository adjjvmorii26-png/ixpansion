"""Wave 798 hush_afterglow — silent afterglow compression."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave798_hush_afterglow as w798


def test_798_vitals_and_glow():
    w798.DATA.mkdir(parents=True, exist_ok=True)
    w798.STATE_FILE.write_text(
        '{"wave":798,"name":"hush_afterglow","glows":0,"status":"test"}'
    )
    v = w798.coherence_vitals()
    assert v["wave"] == 798
    assert v["ok"] is True
    assert "wave795_residual_echo_filter" in w798.resonates_with()
    r = w798.handler({"action": "glow", "text": "council hush", "age": 3, "hour": 6})
    assert r["status"] == "glowing"
    assert r["phase"] == "dawn"
    assert r["token"]
    assert r["payload"] is None
    assert r["audio"] is False
    assert r["surface"] == "silence"
