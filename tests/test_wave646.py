"""Tests for Wave 646 — Negotiation Engine."""
import pytest
from api.wave646_negotiation import handler, coherence_vitals, resonates_with
@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    st = Path("data/wave646_negotiation.json")
    if st.exists(): st.unlink()
    yield
    if st.exists(): st.unlink()
class TestHandler:
    def test_status(self):
        r = handler({}); assert r["ok"] is True; assert r["proposals"] == 0
    def test_propose(self):
        r = handler({"action": "propose", "topic": "share data", "offerer": "alpha", "terms": {"data": "yes"}})
        assert r["ok"] is True; assert r["proposal_id"] == 0
    def test_accept(self):
        handler({"action": "propose", "topic": "x", "offerer": "a"})
        r = handler({"action": "accept", "proposal_id": 0})
        assert r["ok"] is True; assert r["status"] == "accepted"
    def test_accept_missing(self):
        r = handler({"action": "accept", "proposal_id": 99}); assert r["ok"] is False
    def test_agreement_count(self):
        handler({"action": "propose", "topic": "x", "offerer": "a"})
        handler({"action": "accept", "proposal_id": 0})
        r = handler({"action": "status"}); assert r["agreements"] == 1
    def test_unknown(self):
        r = handler({"action": "qux"}); assert r["ok"] is False
class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals(); assert v["wave"] == 646
class TestResonates:
    def test_list(self):
        assert "wave645_communication" in resonates_with()
