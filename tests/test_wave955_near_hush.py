"""Wave 955 near_hush tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave955_near_hush as w


def test_near_hush():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "hush"})
    assert r["status"] == "hushed"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["scores"] is None
    assert r["names"] is None
    assert r["pairs"] is None
    assert r["surface"] == "silence"
    # sealed milles 761,734,718,689,802; pairs under 40: 29, 16, 27
    assert r["near"] == 3
    assert r["threshold"] == 40
    assert r["width"] == 5
    assert "harmony" not in r["caption"]
    custom = w.handler({"action": "hush", "scores": [0.2, 0.21, 0.9], "threshold": 30})
    assert custom["near"] == 1
    assert custom["hushes"] == 2
    cap = w.handler({"action": "caption"})
    assert cap["caption"] == "near 1"
    v = w.coherence_vitals()
    assert v["wave"] == 955
    assert v["ok"] is True
    assert "wave954_score_ash" in w.resonates_with()
    assert "wave671_harmony_braid" in w.resonates_with()
    unknown = w.handler({"action": "replay"})
    assert unknown["status"] == "unknown_action"
