"""Tests for Wave 85 — Adaptive Regulation."""
import pytest
from pathlib import Path
from api.wave85_adaptive_regulation import (
    AdaptiveRegulator, coherence_vitals, handler,
)


class TestAdaptiveRegulator:
    def test_exploration_mode(self):
        reg = AdaptiveRegulator()
        result = reg.regulate(0.85, 0.1)
        assert result["mode"] == "exploration"
        assert "SPAWN_NEW_MODULE" in result["actions"]

    def test_healing_mode(self):
        reg = AdaptiveRegulator()
        result = reg.regulate(0.3)
        assert result["mode"] == "healing"
        assert "RESTORE_VAULT" in result["actions"]

    def test_mutation_mode(self):
        reg = AdaptiveRegulator()
        result = reg.regulate(0.5, 0.6)
        assert result["mode"] == "mutation"
        assert "REWRITE_RULE" in result["actions"]

    def test_behavior_profile(self):
        reg = AdaptiveRegulator()
        for _ in range(5):
            reg.regulate(0.7)
        profile = reg.get_behavior_profile()
        assert profile["total_cycles"] == 5
        assert "mode_distribution" in profile

    def test_classify_context(self):
        reg = AdaptiveRegulator()
        assert reg.classify_context(0.8, 0.1) == "exploration"
        assert reg.classify_context(0.3, 0.0) == "healing"
        assert reg.classify_context(0.5, 0.6) == "mutation"


class TestAdaptiveRegulationHandler:
    def test_status(self):
        result = handler({"action": "status"})
        assert result["wave"] == 85

    def test_regulate(self):
        result = handler({"action": "regulate", "coherence": 0.8, "divergence": 0.1})
        assert result["action"] == "regulate"
        assert result["mode"] in ("exploration", "healing", "mutation")

    def test_profile(self):
        handler({"action": "regulate", "coherence": 0.7})
        result = handler({"action": "profile"})
        assert result["action"] == "profile"
        assert "current_mode" in result

    def test_unknown_action(self):
        result = handler({"action": "bogus"})
        assert "error" in result
