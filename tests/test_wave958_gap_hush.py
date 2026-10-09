"""Wave 958 gap_hush tests. Lab gate only."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave958_gap_hush as w


def test_gap_hush():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":958,"name":"gap_hush","compressions":0,"digest":"","status":"test"}'
    )
    rests = w.score_rests()
    assert [row["milli"] for row in rests] == [29, 16, 27, 41]
    assert rests[0]["pair"] == "674-673"
    assert rests[-1]["pair"] == "671-675"
    assert w.gap_digest(rests) == "eb41e4f84bacd082"
    r = w.handler({"action": "compress"})
    assert r["status"] == "compressed"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert r["digest"] == "eb41e4f84bacd082"
    assert r["span_milli"] == 113
    assert r["widest"] == "671-675"
    v = w.coherence_vitals()
    assert v["wave"] == 958
    assert v["ok"] is True
    assert v["rests"] == 4
    links = w.resonates_with()
    assert "wave671_harmony_braid" in links
    assert "wave675_consensus_bloom" in links
    cap = w.handler({"action": "caption"})
    assert cap["audio"] is False
    assert "rests" in cap["caption"]
