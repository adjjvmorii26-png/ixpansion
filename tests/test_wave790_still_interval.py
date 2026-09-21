"""Wave 790 still_interval tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))

import wave790_still_interval as w790


def test_vitals_contract():
    v = w790.coherence_vitals()
    assert v["wave"] == 790
    assert v["name"] == "still_interval"
    assert v["ok"] is True
    assert v["surface"] == "silence"
    assert v["audio"] is False
    assert "wave772_afterimage_well" in w790.resonates_with()


def test_mark_and_still():
    first = w790.handler({"action": "mark", "note": "pulse_a"})
    assert first["status"] == "marked"
    assert first["gap"]["hash"]
    second = w790.handler({"action": "mark", "note": "pulse_b"})
    assert second["status"] == "marked"
    assert second["gap"]["seconds"] >= 0
    still = w790.handler({"action": "still"})
    assert still["status"] == "still"
    assert still["median_seconds"] >= 0
    assert still["audio"] is False
