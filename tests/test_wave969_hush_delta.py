"""Wave 969 hush_delta — silence increment between residues."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave969_hush_delta as w969


def test_hush_delta_contract():
    vitals = w969.coherence_vitals()
    assert vitals["wave"] == 969
    assert vitals["surface"] == "silence"
    assert "wave968_pulse_residue" in w969.resonates_with()

    r = w969.handler({
        "action": "delta",
        "residue": "a1b2c3d4e5f6",
    })
    assert r["status"] == "delted"
    assert len(r["delta"]) == 10
    assert r["audio"] is False
    assert r["payload"] is None

    cap = w969.handler({"action": "caption"})
    assert "hush" in cap["caption"]
