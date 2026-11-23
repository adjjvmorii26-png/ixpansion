"""Small test for wave 953 memory_fold. Lab gates ≠ ALEPH CI."""
import pytest

def test_memory_fold_contract():
    from api.wave953_memory_fold import handler, coherence_vitals, resonates_with
    vitals = coherence_vitals()
    assert vitals["wave"] == 953
    assert vitals["ok"] is True
    assert "surface" in vitals
    assert "memory_fold" in vitals["module"]
    res = resonates_with()
    assert isinstance(res, list) and len(res) > 0
    out = handler({"action": "status"})
    assert out["audio"] is False
    assert out["surface"] == "silence"
    folded = handler({"action": "fold", "pulses": ["a", "b", "c"]})
    assert folded["status"] == "folded"
    assert "token" in folded
    assert folded["audio"] is False
