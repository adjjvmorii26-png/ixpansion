"""Small contract test for wave 776 hush_ledger."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOD_PATH = ROOT / "api" / "wave776_hush_ledger.py"


def _load():
    spec = importlib.util.spec_from_file_location("wave776", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_contract():
    m = _load()
    assert callable(m.handler)
    assert callable(m.coherence_vitals)
    assert callable(m.resonates_with)
    v = m.coherence_vitals()
    assert v["wave"] == 776
    assert v["ok"] is True
    assert v["surface"] == "silence"
    res = m.resonates_with()
    assert isinstance(res, list) and len(res) >= 1
    out = m.handler({"action": "status"})
    assert out["status"] == "silent" or out.get("status") in ("silent", "compressed")
    assert out.get("audio") is False


def test_pulse_and_ledger():
    m = _load()
    p = m.handler({"action": "pulse", "intensity": 0.5, "duration": 2.0})
    assert p["status"] == "pulsed"
    assert "token" in p
    assert p["audio"] is False
    led = m.handler({"action": "ledger"})
    assert led["status"] == "ledger"
    assert len(led.get("recent") or []) >= 1
