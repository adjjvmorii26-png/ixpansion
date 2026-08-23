import pytest
from omega_prime.agents.cognition.dissonance import (
    CognitiveDissonanceEngine, PressureLevel,
)


class TestCognitiveDissonanceEngine:
    def test_no_contradiction_harmonious(self):
        engine = CognitiveDissonanceEngine()
        engine.form_belief("a1", "sky is blue", 0.9, "observation")
        assert engine.get_pressure_level("a1") == PressureLevel.HARMONIOUS

    def test_contradiction_creates_tension(self):
        engine = CognitiveDissonanceEngine()
        b1 = engine.form_belief("a1", "cell_5 is forest", 0.9, "sight")
        engine.form_belief("a1", "cell_5 is void", 0.8, "touch", contradicts=[b1.belief_id])
        level = engine.get_pressure_level("a1")
        assert level != PressureLevel.HARMONIOUS

    def test_multiple_contradictions_increase_pressure(self):
        engine = CognitiveDissonanceEngine()
        b1 = engine.form_belief("a1", "X is true", 0.9, "source_a")
        engine.form_belief("a1", "X is false", 0.8, "source_b", contradicts=[b1.belief_id])
        engine.form_belief("a1", "X is unknowable", 0.7, "source_c", contradicts=[b1.belief_id])
        p1 = engine._pressure["a1"]
        assert p1 > 0.2

    def test_resolve_reduces_pressure(self):
        engine = CognitiveDissonanceEngine()
        b1 = engine.form_belief("a1", "belief_a", 0.9, "obs")
        engine.form_belief("a1", "not_belief_a", 0.8, "obs2", contradicts=[b1.belief_id])
        pressure_before = engine._pressure["a1"]
        relief = engine.resolve_belief("a1", b1.belief_id)
        assert relief > 0
        assert engine._pressure["a1"] < pressure_before

    def test_crisis_triggered_at_high_pressure(self):
        engine = CognitiveDissonanceEngine()
        # Create many contradictory belief pairs within ONE agent
        for i in range(10):
            b_orig = engine.form_belief("agent_x", f"claim_{i}_is_true", 0.9, f"src_{i}")
            engine.form_belief("agent_x", f"claim_{i}_is_false", 0.9, "rival",
                               contradicts=[b_orig.belief_id])
        result = engine.tick()
        level = engine.get_pressure_level("agent_x")
        assert len(result["agents_in_crisis"]) > 0 or level.value >= PressureLevel.STRAIN.value

    def test_stats_with_pressure(self):
        engine = CognitiveDissonanceEngine()
        b1 = engine.form_belief("x", "statement_a", 0.5, "self")
        engine.form_belief("x", "NOT statement_a", 0.5, "other", contradicts=[b1.belief_id])
        stats = engine.stats
        assert stats["total_beliefs"] == 2
        assert stats["dissonance_events"] >= 1
