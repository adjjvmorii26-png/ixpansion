"""Waves 795–797 tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave795_residual_echo_filter as w795
import wave796_circadian_dawn_pulse as w796
import wave797_antimeme_scar_fuse as w797


def test_795_filter():
    w795.DATA.mkdir(parents=True, exist_ok=True)
    w795.STATE_FILE.write_text(
        '{"wave":795,"name":"residual_echo_filter","filters":0,"status":"test"}'
    )
    r = w795.handler({"action": "filter", "text": "x", "age": 10})
    assert r["status"] in ("kept", "damped")
    assert r["audio"] is False


def test_796_pulse():
    w796.DATA.mkdir(parents=True, exist_ok=True)
    w796.STATE_FILE.write_text(
        '{"wave":796,"name":"circadian_dawn_pulse","pulses":0,"status":"test"}'
    )
    r = w796.handler({"action": "pulse", "hour": 6})
    assert r["phase"] == "dawn"
    assert r["status"] == "pulsed"


def test_797_fuse():
    w797.DATA.mkdir(parents=True, exist_ok=True)
    w797.STATE_FILE.write_text(
        '{"wave":797,"name":"antimeme_scar_fuse","fuses":0,"status":"test"}'
    )
    r = w797.handler({"action": "fuse", "text": "council green hush"})
    assert r["status"] in ("silenced", "cleared")
    assert r["payload"] is None
