"""Wave 972 hush_vector — residual silence orientation."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave972_hush_vector as w972

def test_972_hush_vector():
    assert w972.coherence_vitals()["wave"] == 972
    assert "wave971_threshold_silence" in w972.resonates_with()
    r = w972.handler({"action": "record", "a": "organ_alpha", "b": "organ_beta", "hush": 0.82})
    assert r["status"] == "recorded"
    assert r["vectors"] >= 1
    s = w972.handler({"action": "status"})
    assert s["status"] == "oriented"
    assert s["quietest"] is not None
