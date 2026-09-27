"""Wave 938 pulse_compress tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave938_pulse_compress as w938


def test_938_contract():
    v = w938.coherence_vitals()
    assert v["wave"] == 938
    assert v["name"] == "pulse_compress"
    assert v["ok"] is True
    assert v["surface"] == "silence"
    assert "wave821_still_interval" in w938.resonates_with()
    assert "wave937_experiment_track_hygiene" in w938.resonates_with()


def test_938_fold_is_silent_memory():
    w938.DATA.mkdir(parents=True, exist_ok=True)
    w938.STATE_FILE.write_text(
        '{"wave":938,"name":"pulse_compress","folds":0,"last_hash":"","status":"test"}'
    )
    r = w938.handler({
        "action": "fold",
        "frontier": 938,
        "lab_ok": True,
        "aleph_blocked": False,
        "council": "session_22",
    })
    assert r["status"] == "folded"
    assert r["audio"] is False
    assert r["surface"] == "silence"
    assert r["payload"] is None
    assert r["compressed"]["token"] == "hold"
    assert len(r["compressed"]["hash"]) == 16
    cap = w938.handler({"action": "caption"})
    assert "pulse compress" in cap["caption"]
    assert cap["audio"] is False
