"""Small contract test for Wave 976 Quiet Archive.
Lab gates ≠ ALEPH CI. Additive only.
"""
import importlib.util
from pathlib import Path

def _load_mod():
    p = Path(__file__).resolve().parent.parent / "api" / "wave976_quiet_archive.py"
    spec = importlib.util.spec_from_file_location("wave976_quiet_archive", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_contract():
    mod = _load_mod()
    assert callable(mod.handler)
    assert callable(mod.coherence_vitals)
    assert callable(mod.resonates_with)
    v = mod.coherence_vitals()
    assert v["wave"] == 976
    assert v["ok"] is True
    assert v["surface"] == "silence"
    r = mod.handler({"action": "status"})
    assert r["audio"] is False
    r2 = mod.handler({"action": "archive", "silence_ms": 500, "note": "test"})
    assert r2["status"] == "archived"
    assert "token" in r2
    assert len(r2["token"]) == 10
    assert r2["payload"] is None

if __name__ == "__main__":
    test_contract()
    print("ok")
