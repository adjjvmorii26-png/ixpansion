"""Waves 815–816 tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT))

import wave815_stack_orchestrator as w815
import wave816_ci_gate_mirror as w816


def test_815_run():
    w815.DATA.mkdir(parents=True, exist_ok=True)
    w815.STATE_FILE.write_text(
        '{"wave":815,"name":"stack_orchestrator","runs":0,"status":"test"}'
    )
    r = w815.handler({"action": "run", "question": "does silence scale?"})
    assert r["status"] == "ran"
    assert r["audio"] is False


def test_816_check():
    w816.DATA.mkdir(parents=True, exist_ok=True)
    w816.STATE_FILE.write_text(
        '{"wave":816,"name":"ci_gate_mirror","checks":0,"status":"test"}'
    )
    r = w816.handler({"action": "check"})
    assert r["status"] == "checked"
