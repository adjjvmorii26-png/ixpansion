"""Lab test for Wave 951 silence_threshold."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave951_silence_threshold as w951

def test_silence_threshold_contract():
    assert w951.coherence_vitals()["wave"] == 951
    assert w951.coherence_vitals()["module"] == "wave951_silence_threshold"
    assert "wave950_hush_margin" in w951.resonates_with()

def test_threshold_seals_on_cross():
    r = w951.handler({"action": "threshold", "margin": 2, "threshold": 1})
    assert r["status"] == "sealed"
    assert r["crossed"] is True
    assert r["token"] is not None
    assert r["payload"] is None
    assert r["audio"] is False
    assert r["surface"] == "silence"
    assert r["seals"] >= 1

def test_below_threshold_no_seal():
    r = w951.handler({"action": "threshold", "margin": 0, "threshold": 2})
    assert r["status"] == "below"
    assert r["crossed"] is False
    assert r["token"] is None
    assert r["audio"] is False
