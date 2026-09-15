"""Tests for Wave 666 — Citizen Rights."""
import pytest
from api.wave666_citizen_rights import handler, coherence_vitals, resonates_with
@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    st = Path("data/wave666_citizen_rights.json")
    if st.exists(): st.unlink()
    yield
    if st.exists(): st.unlink()
class TestHandler:
    def test_status(self):
        r = handler({}); assert r["ok"] is True; assert r["citizens"] == 0
    def test_register(self):
        r = handler({"action": "register", "citizen": "cortex", "role": "steward"})
        assert r["ok"] is True; assert "govern" in r["citizen"]["rights"]
    def test_grant(self):
        handler({"action": "register", "citizen": "cortex"})
        r = handler({"action": "grant", "citizen": "cortex", "right": "evolve"})
        assert r["ok"] is True; assert "evolve" in r["rights"]
    def test_revoke(self):
        handler({"action": "register", "citizen": "cortex"})
        handler({"action": "grant", "citizen": "cortex", "right": "evolve"})
        r = handler({"action": "revoke", "citizen": "cortex", "right": "evolve"})
        assert r["ok"] is True; assert "evolve" not in r["rights"]
    def test_can(self):
        handler({"action": "register", "citizen": "cortex", "role": "worker"})
        r = handler({"action": "can", "citizen": "cortex", "right": "sense"})
        assert r["ok"] is True; assert r["permitted"] is True
    def test_can_unregistered(self):
        r = handler({"action": "can", "citizen": "ghost", "right": "sense"})
        assert r["ok"] is True; assert r["permitted"] is False
    def test_census(self):
        handler({"action": "register", "citizen": "cortex"})
        r = handler({"action": "census"}); assert r["ok"] is True; assert r["count"] == 1
    def test_unknown(self):
        r = handler({"action": "foo"}); assert r["ok"] is False
class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals(); assert v["wave"] == 666
class TestResonates:
    def test_list(self):
        assert "wave665_mycelial_network" in resonates_with()
