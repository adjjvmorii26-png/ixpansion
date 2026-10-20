"""Wave 968 pulse_residue — compress captions into silent residue."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave968_pulse_residue as w968


def test_pulse_residue_contract():
    vitals = w968.coherence_vitals()
    assert vitals["wave"] == 968
    assert vitals["surface"] == "silence"
    assert "wave967_still_interval" in w968.resonates_with()

    r = w968.handler({
        "action": "compress",
        "captions": ["still interval · 8.2s", "ci sentinel · lab_noise"],
    })
    assert r["status"] == "compressed"
    assert len(r["residue"]) == 12
    assert r["audio"] is False
    assert r["payload"] is None

    cap = w968.handler({"action": "caption"})
    assert "residue" in cap["caption"]
