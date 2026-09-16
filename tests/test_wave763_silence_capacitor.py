"""Wave 763 silence_capacitor — contract + compression-as-memory."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave763_silence_capacitor as w763


def test_vitals_and_resonance():
    v = w763.coherence_vitals()
    assert v["wave"] == 763
    assert v["name"] == "silence_capacitor"
    assert v["ok"] is True
    peers = w763.resonates_with()
    assert "wave736_silent_broadcast_lattice" in peers
    assert "wave762_dream_compiler" in peers


def test_hold_compress_discharge():
    held = w763.handler({"action": "hold", "text": "unsaid pulse for the loop"})
    assert held["status"] == "held"
    folded = w763.handler({"action": "compress"})
    assert folded["status"] == "compressed"
    assert folded["folded"] >= 1
    out = w763.handler({"action": "discharge"})
    assert out["status"] == "discharged"
    assert out["audio"] is False
    assert out["caption"]
