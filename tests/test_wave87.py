"""Tests for Wave 87 — Coherence Integration."""
import pytest
from pathlib import Path
from api.wave87_coherence_integration import (
    CoherenceIntegrator, CoherencePolicy, coherence_vitals, handler,
)


class TestCoherencePolicy:
    def test_evaluate_basic(self):
        policy = CoherencePolicy()
        result = policy.evaluate(
            {"average_coherence": 0.7},
            {"mode": "exploration"},
            {"recent_coherence": 0.6},
        )
        assert "policy_score" in result
        assert "action" in result

    def test_stable_policy(self):
        policy = CoherencePolicy()
        result = policy.evaluate(
            {"average_coherence": 0.85},
            {"mode": "exploration"},
            {"recent_coherence": 0.75},
        )
        assert result["stable"] == True

    def test_divergent_policy(self):
        policy = CoherencePolicy()
        result = policy.evaluate(
            {"average_coherence": 0.3},
            {"mode": "healing"},
            {"recent_coherence": 0.2},
        )
        assert result["divergent"] or not result["stable"]

    def test_mode_scores(self):
        policy = CoherencePolicy()
        assert policy._mode_score("exploration") == 0.8
        assert policy._mode_score("healing") == 0.4
        assert policy._mode_score("mutation") == 0.6

    def test_determine_action_sustain(self):
        policy = CoherencePolicy()
        action = policy._determine_action(0.9, "exploration", 0.8)
        assert action == "sustain"

    def test_determine_action_regulate(self):
        policy = CoherencePolicy()
        action = policy._determine_action(0.3, "healing", 0.2)
        assert action == "regulate"


class TestCoherenceIntegrator:
    def test_init(self):
        integrator = CoherenceIntegrator()
        assert integrator.cycle == 0
        assert integrator.last_action == "init"

    def test_integrate(self):
        integrator = CoherenceIntegrator()
        result = integrator.integrate(
            {"action": "status"},
            {"action": "status"},
            {"action": "status"},
        )
        assert "action" in result
        assert "policy_score" in result

    def test_get_policy(self):
        integrator = CoherenceIntegrator()
        policy = integrator.get_policy()
        assert "target_coherence" in policy
        assert "last_action" in policy

    def test_timeline(self):
        integrator = CoherenceIntegrator()
        integrator.integrate({"action": "status"}, {"action": "status"}, {"action": "status"})
        timeline = integrator.get_integration_timeline()
        assert isinstance(timeline, list)

    def test_reset(self):
        integrator = CoherenceIntegrator()
        integrator.integrate({"action": "status"}, {"action": "status"}, {"action": "status"})
        integrator.reset()
        assert integrator.cycle == 0
        assert integrator.last_action == "init"


class TestCoherenceIntegrationHandler:
    def test_status(self):
        result = handler({"action": "status"})
        assert result["wave"] == 87

    def test_integrate(self):
        result = handler({"action": "integrate"})
        assert result["action"] == "integrate"

    def test_policy(self):
        result = handler({"action": "policy"})
        assert result["action"] == "policy"

    def test_timeline(self):
        # Add some integration history first
        handler({"action": "integrate"})
        handler({"action": "integrate"})
        result = handler({"action": "timeline"})
        assert result["action"] == "timeline"

    def test_reset(self):
        result = handler({"action": "reset"})
        assert result["action"] == "reset"

    def test_unknown_action(self):
        result = handler({"action": "bogus"})
        assert "error" in result


def test_coherence_vitals_wave87():
    v = coherence_vitals()
    assert v["organ"] == "wave87_coherence_integration"
    assert v["wave"] == 87
    assert v["status"] == "active"
