"""Tests for Wave 655 — Priority Scheduler."""
import pytest
from api.wave655_priority_scheduler import handler, coherence_vitals, resonates_with
@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    st = Path("data/wave655_priority_scheduler.json")
    if st.exists(): st.unlink()
    yield
    if st.exists(): st.unlink()
class TestHandler:
    def test_status(self):
        r = handler({}); assert r["ok"] is True; assert r["queued"] == 0
    def test_queue(self):
        r = handler({"action": "queue", "name": "build", "priority": 2})
        assert r["ok"] is True; assert r["position"] == 0
    def test_run_high_priority_first(self):
        handler({"action": "queue", "name": "low", "priority": 10})
        handler({"action": "queue", "name": "high", "priority": 1})
        r = handler({"action": "run"})
        assert r["ok"] is True; assert r["task"]["name"] == "high"
    def test_drain(self):
        handler({"action": "queue", "name": "a"})
        handler({"action": "queue", "name": "b"})
        r = handler({"action": "drain"}); assert r["ok"] is True; assert r["drained"] == 2
    def test_stats(self):
        handler({"action": "queue", "name": "x", "priority": 5})
        r = handler({"action": "stats"}); assert r["ok"] is True; assert r["avg_priority"] == 5.0
    def test_unknown(self):
        r = handler({"action": "foo"}); assert r["ok"] is False
class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals(); assert v["wave"] == 655
class TestResonates:
    def test_list(self):
        assert "wave654_orchestration_engine" in resonates_with()
