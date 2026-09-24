"""Wave 822 gate_priority tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave822_gate_priority as w822


def test_822_contract():
    v = w822.coherence_vitals()
    assert v["wave"] == 822
    assert v["name"] == "gate_priority"
    assert v["ok"] is True
    assert "wave821_still_interval" in w822.resonates_with()


def test_822_rule_merge_over_noise():
    w822.DATA.mkdir(parents=True, exist_ok=True)
    w822.STATE_FILE.write_text(
        '{"wave":822,"name":"gate_priority","rulings":0,"status":"test"}'
    )
    r = w822.handler(
        {
            "action": "rule",
            "checks": {
                "gate": True,
                "council-smoke": True,
                "boot": True,
                "smoke": True,
                "graft": True,
                "lint": True,
                "test": True,
                "ghas": True,
            },
        }
    )
    assert r["status"] == "ruled"
    assert r["audio"] is False
    assert r["surface"] == "silence"
    assert r["ruling"]["lab_ok"] is True
    assert r["ruling"]["merge_ok"] is True
    assert r["ruling"]["token"] == "merge_over_noise"
    cap = w822.handler({"action": "caption"})
    assert "gate priority" in cap["caption"]


def test_822_hold_when_lab_red():
    r = w822.handler(
        {
            "action": "rule",
            "checks": {
                "gate": False,
                "council-smoke": True,
                "boot": True,
                "smoke": True,
                "graft": True,
                "lint": True,
            },
        }
    )
    assert r["ruling"]["merge_ok"] is False
    assert r["ruling"]["token"] == "hold"
