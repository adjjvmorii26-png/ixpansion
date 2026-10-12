"""Wave 959 score_ash tests. Lab gate only."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave959_score_ash as w


def test_score_ash():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":959,"name":"score_ash","burns":0,"ash":"","status":"test"}'
    )
    millis = w.sorted_scores()
    assert millis == [689, 718, 734, 761, 802]
    assert w.ash_token(millis) == "89fe581a92984eb2"
    r = w.handler({"action": "burn"})
    assert r["status"] == "ashed"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert r["ash"] == "89fe581a92984eb2"
    assert r["span"] == 113
    v = w.coherence_vitals()
    assert v["wave"] == 959
    assert v["ok"] is True
    assert v["sealed"] == 5
    links = w.resonates_with()
    assert "wave671_harmony_braid" in links
    assert "wave675_consensus_bloom" in links
    cap = w.handler({"action": "caption"})
    assert cap["audio"] is False
    assert "ash" in cap["caption"]
