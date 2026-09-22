"""Waves 800–802 tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave800_lattice_still_composer as w800
import wave801_seam_afterglow_bridge as w801
import wave802_quiet_margin_meter as w802


def test_800_compose():
    w800.DATA.mkdir(parents=True, exist_ok=True)
    w800.STATE_FILE.write_text(
        '{"wave":800,"name":"lattice_still_composer","compositions":0,"status":"test"}'
    )
    r = w800.handler({"action": "compose"})
    assert r["status"] == "composed"
    assert r["audio"] is False


def test_801_bridge():
    w801.DATA.mkdir(parents=True, exist_ok=True)
    w801.STATE_FILE.write_text(
        '{"wave":801,"name":"seam_afterglow_bridge","bridges":0,"status":"test"}'
    )
    r = w801.handler({"action": "bridge"})
    assert r["status"] == "bridged"


def test_802_measure():
    w802.DATA.mkdir(parents=True, exist_ok=True)
    w802.STATE_FILE.write_text(
        '{"wave":802,"name":"quiet_margin_meter","measures":0,"status":"test"}'
    )
    r = w802.handler({"action": "measure", "text": "aaa"})
    assert r["status"] == "measured"
    assert 0.0 <= r["margin"] <= 1.0
