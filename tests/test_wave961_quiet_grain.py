"""Wave 961 quiet_grain — silent compression of unsaid Council Session #22 residue."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave961_quiet_grain as w961


def test_961_quiet_grain():
    vitals = w961.coherence_vitals()
    assert vitals["wave"] == 961
    assert vitals["name"] == "quiet_grain"
    assert vitals["scores"] == 5
    assert vitals["surface"] == "silence"

    r = w961.handler({"action": "grain"})
    assert r["status"] == "grained"
    assert len(r["grain"]) == 12
    assert r["audio"] is False
    assert r["payload"] is None

    # Stable grain
    r2 = w961.handler({"action": "grain"})
    assert r2["grain"] == r["grain"]

    cap = w961.handler({"action": "caption"})
    assert "hush" in cap["caption"] or "unsaid" in cap["caption"]
    assert cap["audio"] is False

    assert w961.resonates_with()
    assert "wave671_harmony_braid" not in open("api/wave961_quiet_grain.py").read()  # no direct call
