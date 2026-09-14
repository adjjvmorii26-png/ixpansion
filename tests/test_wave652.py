"""Tests for Wave 652 — Economy Unifier."""
import pytest
from api.wave652_economy_unifier import handler, coherence_vitals, resonates_with, ECONOMY_MODULES
@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    st = Path("data/wave652_economy_unifier.json")
    if st.exists(): st.unlink()
    yield
    if st.exists(): st.unlink()
class TestHandler:
    def test_status(self):
        r = handler({}); assert r["ok"] is True; assert r["snapshots"] == 0
    def test_flows(self):
        r = handler({"action": "flows"})
        assert r["ok"] is True; assert len(r["modules"]) == len(ECONOMY_MODULES)
    def test_ledger(self):
        r = handler({"action": "ledger"})
        assert r["ok"] is True; assert r["snapshot"]["total"] == len(ECONOMY_MODULES)
    def test_bridge(self):
        r = handler({"action": "bridge"}); assert r["ok"] is True; assert "api.attention_economy" in r["modules"]
    def test_unknown(self):
        r = handler({"action": "foo"}); assert r["ok"] is False
class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals(); assert v["wave"] == 652
class TestResonates:
    def test_list(self):
        assert "wave653_routing_unifier" in resonates_with()
