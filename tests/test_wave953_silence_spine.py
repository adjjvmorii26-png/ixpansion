"""Lab test for Wave 953 silence_spine."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave953_silence_spine as w


def test_silence_spine_contract():
    v = w.coherence_vitals()
    assert v["wave"] == 953
    assert v["name"] == "silence_spine"
    assert v["surface"] == "silence"
    assert "wave950_hush_margin" in w.resonates_with()

    r = w.handler({"action": "append", "wave": 950})
    assert r["status"] == "spined"
    assert r["appended"] == 950
    assert r.get("audio") is False
    assert r.get("payload") is None
    assert r["compressed"]

    r2 = w.handler({"action": "caption"})
    assert "silence" in r2["caption"].lower()
    assert r2.get("audio") is False
