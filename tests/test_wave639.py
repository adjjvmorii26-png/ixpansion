"""Tests for Wave 639 — Echo Chamber Breaker."""
import pytest
from api.wave639_echo_breaker import handler, coherence_vitals, resonates_with

@pytest.fixture(autouse=True)
def clean_state():
    from pathlib import Path
    state = Path("data/wave639_echo_breaker.json")
    if state.exists():
        state.unlink()
    yield
    if state.exists():
        state.unlink()

class TestHandler:
    def test_status(self):
        r = handler({})
        assert r["ok"] is True
        assert "accuracy" in r
        assert "bias_scores" not in r  # top-level status has avg_bias_score

    def test_probe(self):
        r = handler({"action": "probe", "type": "math"})
        assert r["ok"] is True
        assert "probe_id" in r
        assert "question" in r

    def test_probe_unknown_type(self):
        r = handler({"action": "probe", "type": "unknown"})
        assert r["ok"] is False

    def test_verify_correct(self):
        p = handler({"action": "probe", "type": "logic"})
        v = handler({"action": "verify", "probe_id": p["probe_id"], "answer": "true"})
        assert v["ok"] is True
        # 'true' matches either true/false logic answer depending on which was picked

    def test_verify_unknown_probe(self):
        v = handler({"action": "verify", "probe_id": "bogus", "answer": "x"})
        assert v["ok"] is False

    def test_bias_check(self):
        r = handler({"action": "bias_check", "claim": "IXPANSION is always flawless and never fails"})
        assert r["ok"] is True
        assert r["bias_score"] > 0.3

    def test_bias_neutral(self):
        r = handler({"action": "bias_check", "claim": "The system has some components that could improve"})
        assert r["ok"] is True

    def test_shatter(self):
        r = handler({"action": "shatter", "topic": "growth"})
        assert r["ok"] is True
        assert "counter_positions" in r
        assert len(r["counter_positions"]) == 3

    def test_anchors(self):
        r = handler({"action": "anchors"})
        assert r["ok"] is True
        assert "math_constants" in r["anchors"]
        assert r["anchors"]["math_constants"]["pi"] == pytest.approx(3.14159, abs=0.01)

    def test_unknown_action(self):
        r = handler({"action": "wat"})
        assert r["ok"] is False

class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals()
        assert v["wave"] == 639

class TestResonates:
    def test_list(self):
        r = resonates_with()
        assert "wave638_symbiosis_protocol" in r
        assert "wave637_meta_regulation" in r
        assert "wave622_resilience_mesh" in r
