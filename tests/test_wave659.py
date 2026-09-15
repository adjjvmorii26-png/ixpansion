"""Tests for Wave 659 — Epoch Forge."""
import pytest
from api.wave659_epoch_forge import handler, coherence_vitals, resonates_with
@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    st = Path("data/wave659_epoch_forge.json")
    if st.exists(): st.unlink()
    yield
    if st.exists(): st.unlink()
class TestHandler:
    def test_status(self):
        r = handler({}); assert r["ok"] is True; assert r["proposals"] == 0
    def test_propose(self):
        r = handler({"action": "propose", "name": "dream_engine", "entropy": 0.8, "resonance": 0.6})
        assert r["ok"] is True; assert r["proposal"]["status"] == "proposed"; assert r["proposal"]["score"] > 0.5
    def test_merge(self):
        handler({"action": "propose", "name": "a"})
        handler({"action": "propose", "name": "b"})
        r = handler({"action": "merge"})
        assert r["ok"] is True; assert len(r["epoch"]["waves"]) >= 2
    def test_merge_empty(self):
        r = handler({"action": "merge"}); assert r["ok"] is False
    def test_deprecate(self):
        r = handler({"action": "deprecate", "name": "stale_x", "reason": "entropy collapse"})
        assert r["ok"] is True; assert r["deprecated"]["reason"] == "entropy collapse"
    def test_ratify(self):
        handler({"action": "propose", "name": "a"})
        handler({"action": "merge"})
        r = handler({"action": "ratify", "epoch_index": 0})
        assert r["ok"] is True; assert r["epoch"]["status"] == "ratified"
    def test_ratify_missing(self):
        r = handler({"action": "ratify", "epoch_index": 9}); assert r["ok"] is False
    def test_unknown(self):
        r = handler({"action": "foo"}); assert r["ok"] is False
class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals(); assert v["wave"] == 659
class TestResonates:
    def test_list(self):
        assert "wave660_lineage_crystal" in resonates_with()
