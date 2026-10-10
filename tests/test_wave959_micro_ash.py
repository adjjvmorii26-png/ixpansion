"""Wave 959 micro_ash tests. Lab gate only."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave959_micro_ash as w


def test_micro_ash():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":959,"name":"micro_ash","compressions":0,"digest":"","status":"test"}'
    )
    ash = w.product_ash()
    assert abs(ash["product"] - 0.221614795308) < 1e-9
    assert abs(ash["dust"] - 0.000000795308) < 1e-12
    assert w.ash_digest(ash) == "1461e23a67ec2376"
    r = w.handler({"action": "compress"})
    assert r["status"] == "compressed"
    assert r["audio"] is False
    assert r["payload"] is None
    assert r["surface"] == "silence"
    assert r["digest"] == "1461e23a67ec2376"
    assert abs(r["dust"] - 0.000000795308) < 1e-12
    v = w.coherence_vitals()
    assert v["wave"] == 959
    assert v["ok"] is True
    assert v["grains"] == 1
    links = w.resonates_with()
    assert "wave671_harmony_braid" in links
    assert "wave675_consensus_bloom" in links
    cap = w.handler({"action": "caption"})
    assert cap["audio"] is False
    assert "ash" in cap["caption"]
