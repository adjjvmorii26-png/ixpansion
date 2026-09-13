"""Tests for Wave 432 — Vault-Driven Evolution."""
import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from api.wave432_vault_driven_evolution import (
    CoherenceRegulator, VaultOrgan, handler, coherence_vitals
)

def test_coherence_vitals():
    vitals = coherence_vitals()
    assert vitals["organ"] == "wave432_vault_driven_evolution"
    assert vitals["wave"] == 432
    assert "coherence" in vitals
    assert "status" in vitals
    assert vitals["status"] in ["CRITICAL", "WARNING", "HEALTHY", "THRIVING"]

def test_coherence_regulator_init():
    reg = CoherenceRegulator()
    assert reg.coherence == 1.0
    assert reg.thresholds["critical"] == 0.3
    assert reg.entropy_budget == 100.0

def test_coherence_regulator_measure():
    reg = CoherenceRegulator()
    coherence = reg.measure_coherence()
    assert 0.0 <= coherence <= 1.0

def test_coherence_regulator_check_health():
    reg = CoherenceRegulator()
    health = reg.check_health()
    assert "coherence" in health
    assert "mutation_pressure" in health
    assert "status" in health
    assert "timestamp" in health

def test_coherence_regulator_regulate():
    reg = CoherenceRegulator()
    result = reg.regulate()
    assert "health" in result
    assert "actions" in result
    assert result["regulated"] is True

def test_vault_organ_init():
    vault = VaultOrgan("test_vault_001")
    assert vault.vault_id == "test_vault_001"
    assert vault.wave == 432
    assert vault.state == "active"
    assert 0.1 <= vault.resonance <= 1.0

def test_vault_organ_amplify():
    vault = VaultOrgan("test_vault_002")
    original = vault.resonance
    amplified = vault.amplify()
    assert amplified >= original
    assert amplified <= 2.0

def test_vault_organ_trigger_mutation_low():
    vault = VaultOrgan("test_vault_003")
    vault.resonance = 0.5
    result = vault.trigger_mutation()
    assert result is None

def test_vault_organ_trigger_mutation_high():
    vault = VaultOrgan("test_vault_004")
    vault.resonance = 2.0
    result = vault.trigger_mutation()
    assert result is not None
    assert result["mutation_type"] == "resonance_overflow"
    assert "result" in result

def test_vault_organ_to_dict():
    vault = VaultOrgan("test_vault_005")
    d = vault.to_dict()
    assert d["vault_id"] == "test_vault_005"
    assert d["wave"] == 432
    assert "mutation_seed" in d

def test_handler_status():
    result = handler({"action": "status"})
    assert result["action"] == "status"
    assert "coherence" in result
    assert "status" in result

def test_handler_regulate():
    result = handler({"action": "regulate"})
    assert result["action"] == "regulate"
    assert "health" in result
    assert result["regulated"] is True

def test_handler_create_vault():
    result = handler({"action": "create_vault", "vault_id": "test_vault"})
    assert result["action"] == "create_vault"
    assert result["vault"]["vault_id"] == "test_vault"

def test_handler_diagnostics_sweep():
    result = handler({"action": "diagnostics_sweep"})
    assert result["action"] == "diagnostics_sweep"
    assert "total_modules" in result
    assert "healthy_modules" in result
    assert "coherence_regulator" in result

def test_handler_evolve():
    result = handler({"action": "evolve"})
    assert result["action"] == "evolve"
    assert "regulation" in result
    assert "new_vaults" in result

def test_handler_unknown_action():
    result = handler({"action": "unknown_action"})
    assert "error" in result

def test_handler_default_action():
    result = handler({})
    assert result["action"] == "status"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
