"""Tests for Wave 665 — Mycelial Network."""
import pytest
from api.wave665_mycelial_network import handler, coherence_vitals, resonates_with
@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    st = Path("data/wave665_mycelial_network.json")
    if st.exists(): st.unlink()
    yield
    if st.exists(): st.unlink()
class TestHandler:
    def test_status(self):
        r = handler({}); assert r["ok"] is True; assert r["nodes"] == 0
    def test_connect(self):
        r = handler({"action": "connect", "node": "cortex", "neighbors": ["limbic"]})
        assert r["ok"] is True; assert r["node"]["neighbors"] == ["limbic"]
    def test_signal(self):
        r = handler({"action": "signal", "from": "a", "to": "b", "payload": "pulse"})
        assert r["ok"] is True; assert r["signal"]["payload"] == "pulse"; assert r["signal"]["hops"] == 1
    def test_arbitrate(self):
        r = handler({"action": "arbitrate", "claimants": ["b", "a"], "resource": "cpu"})
        assert r["ok"] is True; assert r["arbitration"]["winner"] == "a"
    def test_map(self):
        handler({"action": "connect", "node": "x", "neighbors": ["y"]})
        r = handler({"action": "map"}); assert r["ok"] is True; assert len(r["nodes"]) == 1
    def test_unknown(self):
        r = handler({"action": "foo"}); assert r["ok"] is False
class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals(); assert v["wave"] == 665
class TestResonates:
    def test_list(self):
        assert "wave663_resonance_ledger" in resonates_with()
