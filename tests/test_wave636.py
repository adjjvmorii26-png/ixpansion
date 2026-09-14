"""Tests for Wave 636 — Adaptive Regulation."""
import pytest
from api.wave636_adaptive_regulation import handler, coherence_vitals, resonates_with

@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    state = Path("data/wave636_adaptive_regulation.json")
    if state.exists():
        state.unlink()
    yield
    if state.exists():
        state.unlink()

class TestHandler:
    def test_status(self):
        r = handler({})
        assert r["ok"] is True

    def test_assess_exploration(self):
        r = handler({"action": "assess", "coherence": {"avg_coherence": 0.9, "variance": 0.01}})
        assert r["ok"] is True
        assert r["mode"] == "exploration"

    def test_assess_healing(self):
        r = handler({"action": "assess", "coherence": {"avg_coherence": 0.2, "variance": 0.01}})
        assert r["ok"] is True
        assert r["mode"] == "healing"

    def test_assess_mutation(self):
        r = handler({"action": "assess", "coherence": {"avg_coherence": 0.6, "variance": 0.5}})
        assert r["ok"] is True
        assert r["mode"] == "mutation"

    def test_assess_modules_list(self):
        r = handler({"action": "assess", "coherence": {"modules": {"a": 0.9, "b": 0.8, "c": 0.2}}})
        assert r["ok"] is True
        assert r["mode"] in ("mutation", "healing")

    def test_set_policy(self):
        r = handler({"action": "set_policy", "mode": "healing", "key": "max_new", "value": 0})
        assert r["ok"] is True

    def test_policy_check_blocks(self):
        # In healing mode, creating modules is blocked
        r = handler({"action": "policy_check", "mode": "healing", "action_name": "create_module"})
        assert r["ok"] is True
        assert r["allowed"] is False

    def test_policy_check_allows(self):
        r = handler({"action": "policy_check", "mode": "exploration", "action_name": "create_module"})
        assert r["ok"] is True
        assert r["allowed"] is True

    def test_unknown_action(self):
        r = handler({"action": "zzz"})
        assert r["ok"] is False

class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals()
        assert v["wave"] == 636

class TestResonates:
    def test_list(self):
        assert "wave635_coherence_gradient" in resonates_with()
