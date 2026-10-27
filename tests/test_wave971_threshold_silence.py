"""Wave 971 threshold_silence — lab organ test.
Silence is the product surface. Compression is memory.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave971_threshold_silence as w971

def test_971_threshold_silence():
    vitals = w971.coherence_vitals()
    assert vitals["wave"] == 971
    assert vitals["ok"] is True
    r = w971.handler({"action": "approach", "signal": "edge_probe", "intensity": 0.6})
    assert r["status"] == "approached"
    assert "distance" in r
    status = w971.handler({"action": "status"})
    assert status["status"] == "threshold"
