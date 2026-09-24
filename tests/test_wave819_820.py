"""Waves 819–820 tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave819_forge_ledger_mirror as w819
import wave820_observatory_pulse as w820


def test_819_mirror():
    w819.DATA.mkdir(parents=True, exist_ok=True)
    w819.STATE_FILE.write_text(
        '{"wave":819,"name":"forge_ledger_mirror","mirrors":0,"trail":[],"status":"test"}'
    )
    r = w819.handler({"action": "mirror", "skill": "skillforge", "decision": "hold"})
    assert r["status"] == "mirrored"
    assert r["audio"] is False


def test_820_pulse():
    w820.DATA.mkdir(parents=True, exist_ok=True)
    w820.STATE_FILE.write_text(
        '{"wave":820,"name":"observatory_pulse","pulses":0,"status":"test"}'
    )
    r = w820.handler({"action": "pulse"})
    assert r["status"] == "pulsed"
    assert r["signal"]["wave_count"] >= 1
