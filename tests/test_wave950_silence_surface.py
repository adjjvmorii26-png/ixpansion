"""Small test for wave950 silence_surface organ."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave950_silence_surface as organ

def test_status_and_observe():
    # Reset-ish by calling status
    r = organ.handler({"action": "status"})
    assert r["ok"] is True
    assert r["wave"] == 950
    assert "surface" in r
    # Observe a note
    r2 = organ.handler({"action": "observe", "note": "the gap after the last word"})
    assert r2["status"] == "observed"
    assert r2["surface"] >= 1
    # Compress if enough
    organ.handler({"action": "observe", "note": "another absence"})
    r3 = organ.handler({"action": "compress"})
    assert r3["status"] in ("compressed", "too_sparse")
    print("wave950 silence_surface test passed")

if __name__ == "__main__":
    test_status_and_observe()
