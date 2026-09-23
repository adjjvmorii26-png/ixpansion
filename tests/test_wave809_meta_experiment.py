"""Wave 809 meta_experiment_loop tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave809_meta_experiment_loop as w


def test_diagram_and_advance():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":809,"name":"meta_experiment_loop","layer":"ixpansion","loops":0,"insights":[],"status":"test"}'
    )
    d = w.handler({"action": "diagram"})
    assert d["diagram"][0] == "IXPANSION"
    assert "repeat" in d["diagram"][-1]
    a = w.handler({"action": "advance", "note": "boot"})
    assert a["from"] == "ixpansion" and a["to"] == "experiment_system"
    assert a["audio"] is False


def test_loop_and_insight():
    w.DATA.mkdir(parents=True, exist_ok=True)
    w.STATE_FILE.write_text(
        '{"wave":809,"name":"meta_experiment_loop","layer":"learn_experiment_system","loops":0,"insights":[],"status":"test"}'
    )
    r = w.handler({"action": "advance", "note": "meta"})
    assert r["status"] == "looped"
    assert r["to"] == "ixpansion"
    i = w.handler({"action": "insight", "text": "shorter replay windows"})
    assert i["status"] == "insight_recorded"
