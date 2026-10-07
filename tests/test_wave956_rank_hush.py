"""Wave 956 rank_hush tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave956_rank_hush as w


def test_rank_hush_sealed_council():
    w.DATA.mkdir(parents=True, exist_ok=True)
    if w.STATE_FILE.exists():
        w.STATE_FILE.unlink()
    r = w.handler({"action": "rank"})
    assert r["status"] == "ranked"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    # 761,734,718,689,802 — six inversions, ten pairs. Bloom sits above the floor.
    assert r["inversions"] == 6
    assert r["pairs"] == 10
    assert "score" not in r
    assert "persona" not in r
    again = w.handler({"action": "rank"})
    assert again["inversions"] == 6
    mono = w.handler({"action": "rank", "milles": [1, 2, 3, 4]})
    assert mono["inversions"] == 0
    assert mono["pairs"] == 6
    v = w.coherence_vitals()
    assert v["wave"] == 956
    assert v["ok"] is True
    assert "wave675_consensus_bloom" in w.resonates_with()
    assert "wave954_score_ash" in w.resonates_with()
