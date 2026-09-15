"""Tests for Wave 664 — Paradox Court."""
import pytest
from api.wave664_paradox_court import handler, coherence_vitals, resonates_with
@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    st = Path("data/wave664_paradox_court.json")
    if st.exists(): st.unlink()
    yield
    if st.exists(): st.unlink()
class TestHandler:
    def test_status(self):
        r = handler({}); assert r["ok"] is True; assert r["cases"] == 0
    def test_file(self):
        r = handler({"action": "file", "name": "time_loop", "charge": "temporal_contradiction"})
        assert r["ok"] is True; assert r["case"]["status"] == "filed"
    def test_deliberate(self):
        handler({"action": "file", "name": "time_loop"})
        r = handler({"action": "deliberate", "case_id": 0, "verdict": "harmonize"})
        assert r["ok"] is True; assert r["case"]["status"] == "adjudicated"
    def test_deliberate_missing(self):
        r = handler({"action": "deliberate", "case_id": 9}); assert r["ok"] is False
    def test_verdict(self):
        handler({"action": "file", "name": "x"})
        handler({"action": "deliberate", "case_id": 0})
        r = handler({"action": "verdict"}); assert r["ok"] is True; assert r["adjudicated"] == 1
    def test_precedents(self):
        handler({"action": "file", "name": "x"})
        handler({"action": "deliberate", "case_id": 0})
        r = handler({"action": "precedents"}); assert r["ok"] is True; assert len(r["precedents"]) == 1
    def test_unknown(self):
        r = handler({"action": "foo"}); assert r["ok"] is False
class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals(); assert v["wave"] == 664
class TestResonates:
    def test_list(self):
        assert "wave665_mycelial_network" in resonates_with()
