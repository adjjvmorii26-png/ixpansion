"""Tests for Wave 635 — Coherence Gradient Field."""
import pytest
from api.wave635_coherence_gradient import handler, coherence_vitals, resonates_with

@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    state = Path("data/wave635_coherence_gradient.json")
    if state.exists():
        state.unlink()
    yield
    if state.exists():
        state.unlink()

class TestHandler:
    def test_status(self):
        r = handler({})
        assert r["ok"] is True
        assert r["tick"] == 0

    def test_register(self):
        r = handler({"action": "register", "name": "alpha", "coherence": 0.7})
        assert r["ok"] is True
        assert r["module"] == "alpha"

    def test_connect(self):
        handler({"action": "register", "name": "a"})
        handler({"action": "register", "name": "b"})
        r = handler({"action": "connect", "a": "a", "b": "b", "weight": 0.8})
        assert r["ok"] is True
        assert r["weight"] == 0.8

    def test_tick_flows(self):
        handler({"action": "register", "name": "a", "coherence": 1.0})
        handler({"action": "register", "name": "b", "coherence": 0.0})
        handler({"action": "connect", "a": "a", "b": "b"})
        r = handler({"action": "tick"})
        assert r["ok"] is True
        assert r["tick"] == 1

    def test_perturb(self):
        handler({"action": "register", "name": "x", "coherence": 0.5})
        r = handler({"action": "perturb", "module": "x", "delta": 0.3})
        assert r["ok"] is True
        assert r["new_coherence"] == pytest.approx(0.8, abs=0.01)

    def test_field_map(self):
        handler({"action": "register", "name": "m1"})
        r = handler({"action": "field"})
        assert r["ok"] is True
        assert len(r["field"]) == 1

    def test_gradient_stats(self):
        r = handler({"action": "gradients"})
        assert r["ok"] is True
        assert "total_connections" in r

    def test_unknown_action(self):
        r = handler({"action": "nope"})
        assert r["ok"] is False

class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals()
        assert v["wave"] == 635

class TestResonates:
    def test_list(self):
        r = resonates_with()
        assert "wave634_temporal_field" in r
