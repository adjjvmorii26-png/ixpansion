"""Wave 799 hold_seam — silent seam between afterglow and next pulse."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave799_hold_seam as w799


def test_799_vitals_and_hold():
    w799.DATA.mkdir(parents=True, exist_ok=True)
    w799.STATE_FILE.write_text(
        '{"wave":799,"name":"hold_seam","holds":0,"status":"test"}'
    )
    v = w799.coherence_vitals()
    assert v["wave"] == 799
    assert v["ok"] is True
    assert "wave798_hush_afterglow" in w799.resonates_with()
    r = w799.handler({"action": "hold", "age": 2, "hour": 6})
    assert r["status"] == "holding"
    assert r["phase"] == "dawn"
    assert r["width"] > 0
    assert r["payload"] is None
    assert r["audio"] is False
    assert r["surface"] == "silence"
