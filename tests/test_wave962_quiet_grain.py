"""Lab gate for Wave 962 quiet_grain. Lab ≠ full ALEPH CI."""
from __future__ import annotations

import importlib


def test_status_and_vitals():
    mod = importlib.import_module("api.wave962_quiet_grain")
    v = mod.coherence_vitals()
    assert v["wave"] == 962
    assert v["name"] == "quiet_grain"
    assert v["surface"] == "silence"
    assert v["ok"] is True
    assert "wave950_hush_margin" in mod.resonates_with()
    st = mod.handler({"action": "status"})
    assert st["audio"] is False
    assert st["status"] in ("idle", "grained", "captioned")


def test_grain_action():
    mod = importlib.import_module("api.wave962_quiet_grain")
    out = mod.handler({"action": "grain", "margin": 5})
    assert out["status"] == "grained"
    assert out["audio"] is False
    assert out["surface"] == "silence"
    assert isinstance(out["grain"], int)
    assert out["grain"] >= 12
    assert out["payload"] is None
