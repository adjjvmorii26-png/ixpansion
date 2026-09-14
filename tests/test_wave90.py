"""Tests for Wave 90 — Axiom Forge."""
import pytest
from api.wave90_axiom_forge import (
    Axiom, AxiomForge, coherence_vitals, handler,
)


class TestAxiom:
    def test_init(self):
        ax = Axiom("a1", "test principle", "coherence", 0.8)
        assert ax.axiom_id == "a1"
        assert ax.text == "test principle"
        assert ax.source == "coherence"
        assert ax.gravity == 0.8
        assert ax.adherence == 0.5

    def test_gravity_clamped(self):
        ax = Axiom("a2", "p", "declared", 3.0)
        assert ax.gravity == 1.0
        ax2 = Axiom("a3", "p", "declared", -2.0)
        assert ax2.gravity == 0.0

    def test_to_dict(self):
        ax = Axiom("a4", "p", "memory")
        d = ax.to_dict()
        assert d["axiom_id"] == "a4"
        assert d["source"] == "memory"
        assert "adherence" in d


class TestAxiomForge:
    def test_signal_axiom(self):
        forge = AxiomForge()
        ax = forge.signal_axiom("stay curious", "identity", 0.6)
        assert ax.axiom_id in forge.axioms
        assert forge.canon == [ax.axiom_id]

    def test_derive_axioms(self):
        forge = AxiomForge()
        derived = forge.derive_axioms(
            {"overall_coherence": 0.85, "growth_direction": "evolving",
             "core_values": ["growth", "integrity"]},
            {"recent_coherence": 0.8},
            {"action": "sustain"},
        )
        assert len(derived) >= 3

    def test_derive_low_coherence(self):
        forge = AxiomForge()
        derived = forge.derive_axioms(
            {"overall_coherence": 0.3, "growth_direction": "consolidating",
             "core_values": []},
            {"recent_coherence": 0.2},
            {"action": "regulate"},
        )
        assert len(derived) >= 1

    def test_review(self):
        forge = AxiomForge()
        forge.signal_axiom("p1", "coherence")
        forge.signal_axiom("p2", "identity")
        result = forge.review(0.7)
        assert result["cycle"] == 1
        assert result["axiom_count"] == 2
        assert "avg_adherence" in result

    def test_amend_axiom(self):
        forge = AxiomForge()
        ax = forge.signal_axiom("original text")
        amended = forge.amend_axiom(ax.axiom_id, "new text", "direction shift")
        assert amended is not None
        assert amended.text == "new text"
        assert len(amended.amendments) == 1

    def test_amend_missing(self):
        forge = AxiomForge()
        assert forge.amend_axiom("nope", "x") is None

    def test_constitution(self):
        forge = AxiomForge()
        forge.signal_axiom("p1", "coherence", 0.9)
        forge.signal_axiom("p2", "memory", 0.6)
        constitution = forge.get_constitution()
        assert constitution["axiom_count"] == 2
        assert constitution["total_gravity"] == pytest.approx(1.5)


class TestAxiomForgeHandler:
    def test_status(self):
        result = handler({"action": "status"})
        assert result["wave"] == 90
        assert "forge_temperature" in result

    def test_signal(self):
        result = handler({"action": "signal", "text": "the garden remembers",
                          "source": "memory"})
        assert result["action"] == "signal"
        assert result["axiom"]["text"] == "the garden remembers"

    def test_derive(self):
        result = handler({"action": "derive",
                          "assessment": {"overall_coherence": 0.9,
                                         "growth_direction": "evolving",
                                         "core_values": ["growth"]},
                          "memory": {"recent_coherence": 0.8},
                          "policy": {"action": "sustain"}})
        assert result["action"] == "derive"
        assert len(result["derived"]) >= 1

    def test_review(self):
        handler({"action": "signal", "text": "p"})
        result = handler({"action": "review", "coherence": 0.7})
        assert result["action"] == "review"
        assert result["cycle"] >= 1

    def test_amend(self):
        created = handler({"action": "signal", "text": "old"})
        axiom_id = created["axiom"]["axiom_id"]
        result = handler({"action": "amend", "axiom_id": axiom_id,
                          "new_text": "new", "reason": "growth"})
        assert result["action"] == "amend"
        assert result["axiom"]["text"] == "new"

    def test_constitution(self):
        result = handler({"action": "constitution"})
        assert result["action"] == "constitution"
        assert "axioms" in result

    def test_unknown_action(self):
        result = handler({"action": "bogus"})
        assert "error" in result


def test_coherence_vitals_wave90():
    v = coherence_vitals()
    assert v["organ"] == "wave90_axiom_forge"
    assert v["wave"] == 90
    assert v["status"] == "active"
