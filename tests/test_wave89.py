"""Tests for Wave 89 — Self-Awareness Consciousness Layer."""
import time
import pytest
from pathlib import Path
from api.wave89_self_awareness import (
    SelfCoherenceAssessment, AgentIdentityFormation, SelfAwarenessConsciousness,
    coherence_vitals, handler,
)


class TestSelfCoherenceAssessment:
    def test_assess_basic(self):
        assessment = SelfCoherenceAssessment()
        result = assessment.assess(0.7, 0.8, 0.6, 0.5)
        assert "overall_coherence" in result
        assert "identity_strength" in result
        assert "growth_direction" in result
        assert "core_values" in result
        assert "self_description" in result

    def test_identity_strength(self):
        assessment = SelfCoherenceAssessment()
        result = assessment.assess(0.85, 0.8, 0.8, 0.8)
        assert result["identity_strength"] > 0.5

    def test_growth_direction(self):
        assessment = SelfCoherenceAssessment()
        result = assessment.assess(0.85, 0.8, 0.8, 0.8)
        assert result["growth_direction"] in ("exploring", "evolving", "stabilizing", "consolidating")

    def test_core_values(self):
        assessment = SelfCoherenceAssessment()
        result = assessment.assess(0.85, 0.8, 0.8, 0.8)
        assert isinstance(result["core_values"], list)

    def test_self_description(self):
        assessment = SelfCoherenceAssessment()
        result = assessment.assess(0.85, 0.8, 0.8, 0.8)
        assert "Self:" in result["self_description"]

    def test_get_identity_report(self):
        assessment = SelfCoherenceAssessment()
        assessment.assess(0.7, 0.7, 0.7, 0.7)
        report = assessment.get_identity_report()
        assert "overall_coherence" in report
        assert "identity_strength" in report
        assert "growth_direction" in report

    def test_journal(self):
        assessment = SelfCoherenceAssessment()
        assessment.assess(0.7, 0.7, 0.7, 0.7)
        journal = assessment.get_journal()
        assert isinstance(journal, list)
        assert len(journal) == 1


class TestAgentIdentityFormation:
    def test_update_identity(self):
        identity = AgentIdentityFormation()
        result = identity.update_identity(0.85, 0.8, "evolving")
        assert "identity_tags" in result
        assert "role_concept" in result
        assert "mission_statement" in result

    def test_identity_report(self):
        identity = AgentIdentityFormation()
        identity.update_identity(0.85, 0.8, "evolving")
        result = identity.get_identity_report()
        assert "identity_tags" in result
        assert "role_concept" in result
        assert "mission_statement" in result
        assert "creation_history_count" in result
        assert result["creation_history_count"] == 1


class TestSelfAwarenessConsciousness:
    def test_evaluate_self(self):
        consciousness = SelfAwarenessConsciousness()
        result = consciousness.evaluate_self(0.7, 0.8, 0.6, 0.5)
        assert "self_assessment" in result
        assert "identity_update" in result
        assert "evaluation_timestamp" in result

    def test_set_goal(self):
        consciousness = SelfAwarenessConsciousness()
        result = consciousness.set_goal("explore coherence")
        assert result["goal"] == "explore coherence"
        assert result["status"] == "set"

    def test_consciousness_report(self):
        consciousness = SelfAwarenessConsciousness()
        result = consciousness.get_self_consciousness_report()
        assert "self_assessment" in result
        assert "agent_identity" in result
        assert "last_evaluation" in result


class TestCoherenceIntegrationHandler:
    def test_status(self):
        result = handler({"action": "status"})
        assert result["wave"] == 89
        assert "self_assessment" in result

    def test_evaluate(self):
        result = handler({"action": "evaluate", "gradient_coherence": 0.7,
                          "reg_mode_coherence": 0.8, "mem_recent_coherence": 0.6,
                          "integ_policy_score": 0.5})
        assert result["action"] == "evaluate"
        assert "self_assessment" in result

    def test_goal(self):
        result = handler({"action": "goal", "goal_description": "explore coherence"})
        assert result["action"] == "goal"
        assert result["goal"] == "explore coherence"

    def test_consciousness_report(self):
        result = handler({"action": "consciousness_report"})
        assert result["action"] == "consciousness_report"

    def test_journal(self):
        result = handler({"action": "journal", "last": 5})
        assert result["action"] == "journal"
        assert "journal" in result

    def test_identity(self):
        result = handler({"action": "identity"})
        assert result["action"] == "identity"
        assert "self_assessment" in result
        assert "agent_identity" in result

    def test_unknown_action(self):
        result = handler({"action": "bogus"})
        assert "error" in result


def test_coherence_vitals_wave89():
    v = coherence_vitals()
    assert v["organ"] == "wave89_self_awareness"
    assert v["wave"] == 89
    assert v["status"] == "active"
