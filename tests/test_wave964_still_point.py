"""Lab test for Wave 964 still_point. Silence is the product surface."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave964_still_point as w964

def test_still_point_hold():
    assert w964.coherence_vitals()["wave"] == 964
    assert w964.coherence_vitals()["surface"] == "silence"
    r = w964.handler({"action": "hold", "seconds": 7})
    assert r["ok"] is True
    assert r["duration"] >= 7
    assert len(r["point"]) == 10
    v = w964.coherence_vitals()
    assert v["holds"] >= 1
    assert v["memory"] == "compression"
