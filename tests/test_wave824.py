"""Small test for Wave 824 pulse_caption."""
import pytest
from pathlib import Path

from api.wave824_pulse_caption import handler, coherence_vitals, resonates_with

@pytest.fixture(autouse=True)
def clean_state():
    st = Path("data/wave824_pulse_caption.json")
    if st.exists():
        st.unlink()
    yield
    if st.exists():
        st.unlink()

def test_contract():
    v = coherence_vitals()
    assert v["wave"] == 824
    assert v["ok"] is True
    assert "surface" in v
    assert "wave823_pytest_collection_gate" in resonates_with()

def test_compress_and_caption():
    r = handler({"action": "compress", "notes": "council 22 coherent, frontier 824", "frontier": "824"})
    assert r["status"] == "compressed"
    assert r["caption"].startswith("@CoodingLooop")
    assert r["audio"] is False
    assert r["surface"] == "silence"
    c = handler({"action": "caption"})
    assert c["caption"] == r["caption"]
    v = coherence_vitals()
    assert v["pulses"] == 1
