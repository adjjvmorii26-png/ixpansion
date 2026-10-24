"""Wave 969 dual_track_residue — lab organ test."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave969_dual_track_residue as w969

def test_969_contract():
    v = w969.coherence_vitals()
    assert v["wave"] == 969
    assert v["name"] == "dual_track_residue"
    assert v["surface"] == "silence"
    assert "wave968_pulse_residue" in w969.resonates_with()

def test_969_observe():
    r = w969.handler({"action": "observe", "lab": "smoke_ok", "aleph": "full_pending", "note": "daily pulse"})
    assert r["status"] == "observed"
    assert r["residue"]
    assert r["gap"] > 0
    assert r["audio"] is False
    assert r["payload"] is None

def test_969_caption():
    r = w969.handler({"action": "caption"})
    assert r["status"] == "captioned"
    assert "lab≠ALEPH" in r["caption"]
    assert r["audio"] is False
