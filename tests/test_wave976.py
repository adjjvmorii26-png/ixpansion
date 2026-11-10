"""Small contract test for Wave 976 residual_hush."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parent.parent / "api" / "wave976_residual_hush.py"
    spec = importlib.util.spec_from_file_location("wave976_residual_hush", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_contract():
    m = _load()
    assert callable(m.handler)
    assert callable(m.coherence_vitals)
    assert callable(m.resonates_with)
    v = m.coherence_vitals()
    assert v["wave"] == 976
    assert v["ok"] is True
    assert "wave975_silence_margin" in m.resonates_with()
    r = m.handler({"action": "status"})
    assert r.get("audio") is False
    assert r.get("surface") == "silence"
    d = m.handler({"action": "deposit", "margin": 0.3, "token": "test"})
    assert d["status"] == "deposited"
    assert d["added"] >= 0
    assert d.get("audio") is False
