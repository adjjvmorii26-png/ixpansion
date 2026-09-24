"""Wave 821 still_interval tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave821_still_interval as w821


def test_821_contract():
    v = w821.coherence_vitals()
    assert v["wave"] == 821
    assert v["name"] == "still_interval"
    assert v["ok"] is True
    assert "wave820_observatory_pulse" in w821.resonates_with()


def test_821_still_compresses_dual_track():
    w821.DATA.mkdir(parents=True, exist_ok=True)
    w821.STATE_FILE.write_text(
        '{"wave":821,"name":"still_interval","stills":0,"status":"test"}'
    )
    r = w821.handler({"action": "still", "lab_ok": True, "aleph_noise": True})
    assert r["status"] == "still"
    assert r["audio"] is False
    assert r["surface"] == "silence"
    assert r["compressed"]["token"] == "hold"
    cap = w821.handler({"action": "caption"})
    assert "still interval" in cap["caption"]
