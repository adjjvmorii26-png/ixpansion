"""Tests for Wave 981 — Silence Lens."""
import pytest
from pathlib import Path
from api.wave981_silence_lens import handler, coherence_vitals, resonates_with

@pytest.fixture(autouse=True)
def clean_state():
    st = Path("data/wave981_silence_lens.json")
    if st.exists():
        st.unlink()
    yield
    if st.exists():
        st.unlink()

def test_contract():
    assert callable(handler)
    assert callable(coherence_vitals)
    assert callable(resonates_with)
    v = coherence_vitals()
    assert v["wave"] == 981
    assert v["ok"] is True
    assert "wave980_hush_tide" in resonates_with()

def test_observe_and_compress():
    r1 = handler({"action": "observe", "gap": "unspoken_horizon", "weight": 0.3})
    assert r1["status"] == "observed"
    assert r1["vector"] == pytest.approx(0.7)
    r2 = handler({"action": "observe", "gap": "quiet_edge", "weight": 0.6})
    assert r2["status"] == "observed"
    r3 = handler({"action": "compress"})
    assert r3["status"] == "compressed"
    assert r3["compressions"] == 1
    assert "memory" in r3

def test_status():
    r = handler({"action": "status"})
    assert r["status"] == "active"
    assert r["wave"] == 981
