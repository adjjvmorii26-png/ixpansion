"""Wave 952 void_seed tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave952_void_seed as w


def test_void_seed():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "plant", "margin": 7})
    assert r["status"] == "planted"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert r["token"].startswith("v")
    assert r["seeds"] == 1
    assert r["depth"] >= 1
    v = w.coherence_vitals()
    assert v["wave"] == 952
    assert v["ok"] is True
    assert "wave950_hush_margin" in w.resonates_with()
    assert "wave681_hush_membrane" in w.resonates_with()
