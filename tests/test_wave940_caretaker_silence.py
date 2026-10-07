"""Wave 940 caretaker_silence tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave940_caretaker_silence as w940


def test_940_contract():
    v = w940.coherence_vitals()
    assert v["wave"] == 940
    assert v["name"] == "caretaker_silence"
    assert v["ok"] is True
    assert v["surface"] == "silence"
    assert v["track"] == "lab"
    links = w940.resonates_with()
    assert "wave939_residual_bind" in links
    assert "lab.ops.copilots.council" in links


def test_940_hold_is_silent():
    w940.DATA.mkdir(parents=True, exist_ok=True)
    w940.STATE_FILE.write_text(
        '{"wave":940,"name":"caretaker_silence","holds":0,"main_sha":"","open_prs":0,"status":"test"}'
    )
    r = w940.handler({"action": "hold", "main_sha": "767bd5faaa33", "open_prs": 20})
    assert r["status"] == "held"
    assert r["audio"] is False
    assert r["surface"] == "silence"
    assert r["payload"] is None
    assert r["hold"]["token"] == "quiet"
    assert r["hold"]["main_sha"] == "767bd5faaa33"
    assert r["hold"]["open_prs"] == 20
    cap = w940.handler({"action": "caption"})
    assert "caretaker silence hold" in cap["caption"]
    assert cap["audio"] is False
