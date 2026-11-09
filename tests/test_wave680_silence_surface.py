"""Wave 680 Silence Surface — frontier lab organ."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave680_silence_surface as w680

def test_wave680_silence_surface():
    assert w680.coherence_vitals()["wave"] == 680
    assert w680.coherence_vitals()["persona"] == "HUSH"
    assert "wave672_root_archive" in w680.resonates_with()
    o = w680.handler({"action": "observe", "duration": 2.5, "residual": "faint_noise"})
    assert o["status"] == "observed"
    c = w680.handler({"action": "compress"})
    assert c["status"] == "compressed"
    assert c["score"] > 0
    v = w680.coherence_vitals()
    assert v["ok"] is True
    assert v["residues"] >= 1
