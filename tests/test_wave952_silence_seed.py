"""Wave 952 silence_seed tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave952_silence_seed as w


def test_silence_seed():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "seed", "margin": 1, "token": "abcdef123456"})
    assert r["status"] == "seeded"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert len(r["seed"]) == 8
    assert r["seeds"] == 1
    r2 = w.handler({"action": "seed", "margin": 3})
    assert r2["seeds"] == 2
    assert r2["seed"] != r["seed"]
    v = w.coherence_vitals()
    assert v["wave"] == 952
    assert v["ok"] is True
    assert "wave950_hush_margin" in w.resonates_with()
    assert "wave949_council_witness" in w.resonates_with()
