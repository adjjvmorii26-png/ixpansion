"""Tests for dynamic coherence regulator."""
from coherence_regulator import CoherenceRegulator, handler, coherence_vitals


def test_coherence_vitals():
    v = coherence_vitals()
    assert "coherence" in v
    assert "organism" in v
    assert v["organism"] == "IXPANSION"


def test_measure_coherence():
    reg = CoherenceRegulator()
    co = reg.measure_coherence()
    assert 0 <= co <= 1
    assert len(reg.modules_registered) == 16


def test_check_health():
    reg = CoherenceRegulator()
    health = reg.check_health()
    assert "status" in health
    assert "coherence" in health
    assert "mutation_pressure" in health


def test_regulate():
    reg = CoherenceRegulator()
    result = reg.regulate()
    assert "actions" in result
    assert "health" in result
    assert result["regulated"] is True


def test_handler_status():
    result = handler({"action": "status"})
    assert result["organism"] == "IXPANSION"
    assert "coherence" in result


def test_handler_measure():
    result = handler({"action": "measure"})
    assert result["action"] == "measure"
    assert 0 <= result["coherence"] <= 1


def test_handler_regulate():
    result = handler({"action": "regulate"})
    assert "actions" in result
    assert "health" in result


def test_handler_health():
    result = handler({"action": "health"})
    assert "status" in result
