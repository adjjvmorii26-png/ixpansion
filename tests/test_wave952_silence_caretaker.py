"""Wave 952 silence_caretaker tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave952_silence_caretaker as w


def test_silence_caretaker():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "pulse"})
    assert r["status"] == "pulsed"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert r["pulses"] == 1
    r2 = w.handler({"action": "pulse"})
    assert r2["pulses"] == 2
    v = w.coherence_vitals()
    assert v["wave"] == 952
    assert v["ok"] is True
    assert "wave950_hush_margin" in w.resonates_with()
    assert "wave773_ci_sentinel" in w.resonates_with()
    cap = w.handler({"action": "caption"})
    assert "caretaker" in cap["caption"]
