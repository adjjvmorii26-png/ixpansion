"""Tests for Wave 669 — Paradox Appeal."""
import pytest
from api.wave669_paradox_appeal import handler, coherence_vitals, resonates_with
@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    st = Path("data/wave669_paradox_appeal.json")
    if st.exists(): st.unlink()
    yield
    if st.exists(): st.unlink()
class TestHandler:
    def test_status(self):
        r = handler({}); assert r["ok"] is True; assert "appeals" in r
    def test_file(self):
        r = handler({"action": "file", "name": "p1", "verdict": "resolve"})
        assert r["ok"] is True; assert r["case"]["status"] == "adjudicated"
    def test_appeal(self):
        handler({"action": "file", "name": "p1"})
        r = handler({"action": "appeal", "case_id": 0, "grounds": "new_evidence"})
        assert r["ok"] is True; assert r["appeal"]["status"] == "pending"
    def test_appeal_missing_case(self):
        r = handler({"action": "appeal", "case_id": 99}); assert r["ok"] is False
    def test_review(self):
        handler({"action": "file", "name": "p1"})
        handler({"action": "appeal", "case_id": 0})
        r = handler({"action": "review", "appeal_id": 0, "ruling": "reverse"})
        assert r["ok"] is True; assert r["appeal"]["ruling"] == "reverse"
    def test_docket(self):
        r = handler({"action": "docket"}); assert r["ok"] is True; assert "pending" in r
    def test_rulings(self):
        r = handler({"action": "rulings"}); assert r["ok"] is True
    def test_unknown(self):
        r = handler({"action": "foo"}); assert r["ok"] is False
class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals(); assert v["wave"] == 669
class TestResonates:
    def test_list(self):
        assert "wave664_paradox_court" in resonates_with()
