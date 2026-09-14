"""Tests for Wave 653 — Routing Unifier."""
import pytest
from api.wave653_routing_unifier import handler, coherence_vitals, resonates_with, ROUTING_MODULES
@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    st = Path("data/wave653_routing_unifier.json")
    if st.exists(): st.unlink()
    yield
    if st.exists(): st.unlink()
class TestHandler:
    def test_status(self):
        r = handler({}); assert r["ok"] is True; assert r["maps"] == 0
    def test_map(self):
        r = handler({"action": "map"})
        assert r["ok"] is True; assert len(r["routes"]) == len(ROUTING_MODULES)
    def test_resolve(self):
        r = handler({"action": "resolve", "route": "api.health"})
        assert r["ok"] is True; assert r["found"] is True
    def test_registry(self):
        r = handler({"action": "registry"})
        assert r["ok"] is True; assert r["registry"]["total"] == len(ROUTING_MODULES)
    def test_unknown(self):
        r = handler({"action": "foo"}); assert r["ok"] is False
class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals(); assert v["wave"] == 653
class TestResonates:
    def test_list(self):
        assert "wave652_economy_unifier" in resonates_with()
