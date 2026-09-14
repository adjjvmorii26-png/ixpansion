"""Tests for Wave 644 — Recursive Self-Model."""
import pytest
from api.wave644_self_model import handler, coherence_vitals, resonates_with
@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    st = Path("data/wave644_self_model.json")
    if st.exists(): st.unlink()
    yield
    if st.exists(): st.unlink()
class TestHandler:
    def test_status(self):
        r = handler({}); assert r["ok"] is True; assert r["beliefs"] == 0
    def test_belief(self):
        r = handler({"action": "belief", "key": "invariance", "value": "adaptability", "confidence": 0.9})
        assert r["ok"] is True; assert r["revision"] == 1
    def test_belief_revision(self):
        handler({"action": "belief", "key": "x", "value": "1"})
        r = handler({"action": "belief", "key": "x", "value": "2"})
        assert r["revision"] == 2
    def test_introspect(self):
        r = handler({"action": "introspect"}); assert r["ok"] is True; assert "finding" in r["introspection"]
    def test_unknown(self):
        r = handler({"action": "zzz"}); assert r["ok"] is False
class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals(); assert v["wave"] == 644
class TestResonates:
    def test_list(self):
        assert "wave637_meta_regulation" in resonates_with()
