"""Wave 954 score_ash tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave954_score_ash as w


def test_score_ash():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "compress"})
    assert r["status"] == "ashed"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["scores"] is None
    assert r["names"] is None
    assert r["surface"] == "silence"
    # sealed milles 761,734,718,689,802 — spread only
    assert r["ash"] == 113
    assert r["width"] == 5
    assert "harmony" not in r["caption"]
    custom = w.handler({"action": "compress", "scores": [0.2, 0.9]})
    assert custom["ash"] == 700
    assert custom["compressions"] == 2
    cap = w.handler({"action": "caption"})
    assert cap["caption"] == "ash 700"
    v = w.coherence_vitals()
    assert v["wave"] == 954
    assert v["ok"] is True
    assert "wave671_harmony_braid" in w.resonates_with()
    assert "wave950_hush_margin" in w.resonates_with()
    unknown = w.handler({"action": "replay"})
    assert unknown["status"] == "unknown_action"
