"""Wave 975 silence_margin — residual silence after council witness."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave975_silence_margin as w975

def test_silence_margin_vitals():
    v = w975.coherence_vitals()
    assert v["wave"] == 975
    assert v["name"] == "silence_margin"
    assert v["surface"] == "silence"
    assert "wave949_council_witness" in w975.resonates_with()

def test_silence_margin_measure():
    r = w975.handler({"action": "measure", "token": "a1b2c3d4e5f6"})
    assert r["status"] == "measured"
    assert 0.0 <= r["margin"] <= 1.0
    assert r["audio"] is False
    assert r["surface"] == "silence"

def test_silence_margin_caption():
    r = w975.handler({"action": "caption"})
    assert r["status"] == "captioned"
    assert "hush" in r["caption"] or "margin" in r["caption"]
    assert r["audio"] is False
