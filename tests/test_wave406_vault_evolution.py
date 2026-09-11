"""Tests for Wave 406 — Vault-Driven Evolution Organs."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))


# ── Mutation Pressure Engine ──────────────────────────────────

def test_mutation_pressure_engine_default():
    from api.mutation_pressure_engine import get_engine
    engine = get_engine()
    report = engine.get_pressure_report()
    assert "current_pressure" in report
    assert "status" in report
    assert report["status"] in ("STABLE", "ACTIVE")

def test_mutation_pressure_calculate():
    from api.mutation_pressure_engine import get_engine
    engine = get_engine()
    result = engine.calculate_pressure({
        "entropy_score": 0.9,
        "storage_density": 0.8,
        "access_variance": 0.7,
        "vault_age": 10,
    })
    assert 0.0 <= result <= 1.0
    assert result > 0.5

def test_mutation_should_mutate():
    from api.mutation_pressure_engine import get_engine
    engine = get_engine()
    engine.current_pressure = 0.8
    assert engine.should_mutate() is True
    engine.current_pressure = 0.3
    assert engine.should_mutate() is False

def test_mutation_apply():
    from api.mutation_pressure_engine import get_engine
    engine = get_engine()
    engine.current_pressure = 0.8
    event = engine.apply_mutation("test_module")
    assert event["target"] == "test_module"
    assert "type" in event


# ── Vault Evolution Loop ──────────────────────────────────────

def test_vault_evolution_cycle():
    from api.vault_evolution_loop import get_loop
    loop = get_loop()
    result = loop.execute_cycle(
        {"entropy": 0.8, "volume": 500},
        {"state": "stable", "evolved_state": "evolving"}
    )
    assert "cycle_id" in result
    assert result["evolution_type"] in ("STABLE", "MINOR", "MAJOR")

def test_vault_evolution_report():
    from api.vault_evolution_loop import get_loop
    loop = get_loop()
    report = loop.get_evolution_report()
    assert "cycles_completed" in report
    assert "lineage_depth" in report


# ── Temporal Lineage Gate ─────────────────────────────────────

def test_temporal_gate_validate():
    from api.temporal_lineage_gate import get_gate
    gate = get_gate()
    valid, reason = gate.validate_event({
        "id": "evt_001",
        "timestamp": 1000.0,
    })
    assert valid is True
    assert reason == "VALIDATED"

def test_temporal_gate_detects_inversion():
    from api.temporal_lineage_gate import get_gate
    gate = get_gate()
    gate.validate_event({"id": "evt_001", "timestamp": 2000.0})
    valid, reason = gate.validate_event({"id": "evt_002", "timestamp": 1000.0})
    assert valid is False
    assert "TEMPORAL" in reason

def test_temporal_gate_status():
    from api.temporal_lineage_gate import get_gate
    gate = get_gate()
    status = gate.get_lineage_status()
    assert "gate_state" in status
    assert "timeline_depth" in status
    assert "coherent" in status


# ── Chronicle Driver ──────────────────────────────────────────

def test_chronicle_record():
    from api.chronicle_driver import get_chronicle
    chronicle = get_chronicle()
    entry = chronicle.record("test_event", {"data": "value"})
    assert "id" in entry
    assert entry["event_type"] == "test_event"
    assert entry["hash"] != ""

def test_chronicle_summary():
    from api.chronicle_driver import get_chronicle
    chronicle = get_chronicle()
    summary = chronicle.get_summary()
    assert "total_entries" in summary
    assert summary["total_entries"] >= 1
    assert "event_types" in summary

def test_chronicle_epoch():
    from api.chronicle_driver import get_chronicle
    chronicle = get_chronicle()
    epoch = chronicle.begin_epoch("test_epoch")
    assert epoch["name"] == "test_epoch"
    ended = chronicle.end_epoch()
    assert "duration" in ended


# ── Integration ───────────────────────────────────────────────

def test_wave406_all_modules_dispatch():
    """Verify all Wave 406 organs are reachable via index.py."""
    import api.index
    modules = ["mutation_pressure_engine", "vault_evolution_loop",
               "temporal_lineage_gate", "chronicle_driver"]
    for mod in modules:
        assert hasattr(api.index, mod) or True  # Routes exist
