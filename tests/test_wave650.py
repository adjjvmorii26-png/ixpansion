"""Tests for Wave 650 — Auto-Optimizer."""
import pytest
from api.wave650_auto_optimizer import handler, coherence_vitals, resonates_with
@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    st = Path("data/wave650_auto_optimizer.json")
    if st.exists(): st.unlink()
    yield
    if st.exists(): st.unlink()
class TestHandler:
    def test_status(self):
        r = handler({}); assert r["ok"] is True; assert r["tunables"] == 0
    def test_tune(self):
        r = handler({"action": "tune", "name": "bias", "current": 0.3, "metric": 0.7, "delta": 0.1})
        assert r["ok"] is True; assert r["proposed"] == 0.4; assert r["best"] == 0.3
    def test_tune_best_updates(self):
        handler({"action": "tune", "name": "bias", "current": 0.3, "metric": 0.7})
        r = handler({"action": "tune", "name": "bias", "current": 0.8, "metric": 0.9})
        assert r["ok"] is True; assert r["best"] == 0.8
    def test_recommend(self):
        handler({"action": "tune", "name": "bias", "current": 0.3, "metric": 0.7})
        r = handler({"action": "recommend", "name": "bias"})
        assert r["ok"] is True; assert r["recommended"] == 0.3
    def test_history(self):
        handler({"action": "tune", "name": "bias"})
        r = handler({"action": "history", "name": "bias"}); assert r["ok"] is True; assert len(r["entries"]) == 1
    def test_unknown(self):
        r = handler({"action": "foo"}); assert r["ok"] is False
class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals(); assert v["wave"] == 650
class TestResonates:
    def test_list(self):
        assert "wave651_self_repair" in resonates_with()
