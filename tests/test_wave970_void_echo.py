"""Small test for Wave 970 void_echo."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave970_void_echo as w970

def test_void_echo():
    assert w970.coherence_vitals()["wave"] == 970
    r = w970.handler({"action": "void", "question": "what remains after the bloom settles?"})
    assert r["status"] == "voided"
    assert r["id"]
    s = w970.handler({"action": "status"})
    assert s["status"] == "silent"
    assert s["residues"] >= 1
