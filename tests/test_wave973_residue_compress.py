"""Wave 973 residue_compress — small contract test."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave973_residue_compress as w973

def test_973_residue_compress():
    assert w973.coherence_vitals()["wave"] == 973
    assert "wave972_hush_vector" in w973.resonates_with()
    r = w973.handler({"action": "compress", "residual": "trace of prior hush"})
    assert r["status"] == "compressed"
    assert len(r.get("token", "")) == 12
    assert w973.coherence_vitals()["compressions"] >= 1
