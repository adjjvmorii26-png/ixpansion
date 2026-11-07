"""Minimal contract test for wave 951 silence_fold.

Lab-only. Does not require ALEPH CI.
"""
from api.wave951_silence_fold import handler, coherence_vitals, resonates_with


def test_contract():
    vitals = coherence_vitals()
    assert vitals["wave"] == 951
    assert vitals["ok"] is True
    assert "surface" in vitals
    assert vitals["surface"] == "silence"
    assert isinstance(resonates_with(), list)
    assert len(resonates_with()) > 0


def test_fold_and_status():
    r = handler({"action": "fold", "margins": [3, 6, 9]})
    assert r["status"] == "folded"
    assert r["audio"] is False
    assert r["payload"] is None
    assert "memory" in r
    assert r["surface"] == "silence"

    s = handler({"action": "status"})
    assert s["wave"] == 951
    assert s["ok"] is True
    assert s["audio"] is False
