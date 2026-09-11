# Wave 405 Tests: Storage Vault & Evolution Tracker
"""Tests for Wave 405 - Storage Vault + Storage Protocols + Evolution Tracker."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Storage Vault ─────────────────────────────────────────────────

def test_storage_vault_create():
    from api.storage_vault import get_vault
    vault = get_vault(capacity=100)
    assert vault.capacity == 100
    assert vault.current_items == 0
    assert not vault._locked

def test_storage_vault_store_retrieve():
    from api.storage_vault import get_vault
    vault = get_vault(capacity=50)
    success = vault.store("test_key", {"value": 123, "meta": "test"})
    assert success is True
    result = vault.retrieve("test_key")
    assert result == {"value": 123, "meta": "test"}

def test_storage_vault_missing_key():
    from api.storage_vault import get_vault
    vault = get_vault(capacity=50)
    result = vault.retrieve("nonexistent")
    assert result is None

def test_storage_vault_lock_unlock():
    from api.storage_vault import get_vault
    vault = get_vault(capacity=50)
    vault.lock()
    assert vault._locked is True
    assert vault.store("key", "value") is False
    vault.unlock()
    assert vault._locked is False
    assert vault.store("key", "value") is True

def test_storage_vault_capacity_eviction():
    from api.storage_vault import get_vault
    vault = get_vault(capacity=3)
    vault.store("key1", "val1")
    vault.store("key2", "val2")
    vault.store("key3", "val3")
    assert vault.current_items == 3
    vault.store("key4", "val4")  # Should evict oldest
    assert vault.current_items == 3
    assert vault.retrieve("key1") is None  # Oldest evicted
    assert vault.retrieve("key4") == "val4"

def test_storage_vault_status():
    from api.storage_vault import get_vault
    vault = get_vault(capacity=100)
    vault.store("key1", "val1")
    status = vault.status()
    assert status["vault_id"].startswith("vault_")
    assert status["capacity"] == 100
    assert status["current_items"] == 1
    assert status["total_accesses"] >= 1


# ── Storage Protocols ─────────────────────────────────────────────

def test_storage_protocols_store_retrieve():
    from api.storage_protocols import get_protocols
    protocols = get_protocols()
    success = protocols.store_module_data("test_module", {"type": "agent", "level": 5})
    assert success is True
    data = protocols.retrieve_module_data("test_module")
    assert data == {"type": "agent", "level": 5}

def test_storage_protocols_integrity_check():
    from api.storage_protocols import get_protocols, StorageProtocols
    from api.storage_vault import StorageVault
    # Create fresh vault and protocols to avoid interference
    vault = StorageVault(capacity=50)
    protocols = StorageProtocols(vault)
    protocols.store_module_data("integrity_test", {"checksum": "valid"})
    data = protocols.retrieve_module_data("integrity_test")
    assert data == {"checksum": "valid"}
    assert "_hash_warning" not in data

def test_storage_protocols_missing_module():
    from api.storage_protocols import get_protocols
    protocols = get_protocols()
    data = protocols.retrieve_module_data("nonexistent_module")
    assert data is None

def test_storage_protocols_vault_report():
    from api.storage_protocols import get_protocols
    protocols = get_protocols()
    report = protocols.generate_vault_report()
    assert report["protocol_version"] == "2.3.2"
    assert "vault_id" in report
    assert "capacity" in report
    assert "current_items" in report
    assert "storage_efficiency" in report
    assert 0 <= report["storage_efficiency"] <= 100


# ── Evolution Tracker ─────────────────────────────────────────────

def test_evolution_tracker_record():
    from api.evolution_tracker import get_tracker
    tracker = get_tracker()
    tracker.set_current_wave(405)
    snap = tracker.record_module("test_evo_module", {"feature": "storage"}, "creation")
    assert snap.wave == 405
    assert snap.module_id == "test_evo_module"
    assert snap.mutation_type == "creation"
    assert len(snap.hash_signature) == 16

def test_evolution_tracker_history():
    from api.evolution_tracker import get_tracker, EvolutionTracker
    from api.storage_protocols import StorageProtocols
    from api.storage_vault import StorageVault
    # Fresh tracker
    vault = StorageVault(capacity=50)
    protocols = StorageProtocols(vault)
    tracker = EvolutionTracker(protocols)
    tracker.set_current_wave(405)
    tracker.record_module("history_test", {"v": 1}, "creation")
    tracker.set_current_wave(406)
    tracker.record_module("history_test", {"v": 2}, "mutation", "history_test")
    history = tracker.get_module_history("history_test")
    assert len(history) == 2
    assert history[0].data == {"v": 1}
    assert history[1].data == {"v": 2}
    assert history[1].parent_module == "history_test"

def test_evolution_tracker_mutation_patterns():
    from api.evolution_tracker import get_tracker, EvolutionTracker
    from api.storage_protocols import StorageProtocols
    from api.storage_vault import StorageVault
    vault = StorageVault(capacity=50)
    protocols = StorageProtocols(vault)
    tracker = EvolutionTracker(protocols)
    tracker.set_current_wave(405)
    tracker.record_module("pattern_test", {"v": 1}, "creation")
    tracker.set_current_wave(406)
    tracker.record_module("pattern_test", {"v": 2}, "mutation")
    tracker.set_current_wave(407)
    tracker.record_module("pattern_test", {"v": 3}, "fusion")
    patterns = tracker.analyze_mutation_patterns("pattern_test")
    assert patterns["total_mutations"] == 2
    assert patterns["mutation_types"]["mutation"] == 1
    assert patterns["mutation_types"]["fusion"] == 1
    assert len(patterns["hash_changes"]) == 2

def test_evolution_tracker_lineage():
    from api.evolution_tracker import get_tracker, EvolutionTracker
    from api.storage_protocols import StorageProtocols
    from api.storage_vault import StorageVault
    vault = StorageVault(capacity=50)
    protocols = StorageProtocols(vault)
    tracker = EvolutionTracker(protocols)
    tracker.set_current_wave(405)
    tracker.record_module("root_module", {"base": True}, "creation")
    tracker.set_current_wave(406)
    tracker.record_module("child_module", {"derived": True}, "mutation", "root_module")
    tracker.set_current_wave(407)
    tracker.record_module("grandchild_module", {"deep": True}, "mutation", "child_module")
    tree = tracker.get_lineage_tree("root_module")
    assert tree["module_id"] == "root_module"
    assert len(tree["children"]) == 1
    assert tree["children"][0]["module_id"] == "child_module"
    assert len(tree["children"][0]["children"]) == 1
    assert tree["children"][0]["children"][0]["module_id"] == "grandchild_module"

def test_evolution_tracker_wave_report():
    from api.evolution_tracker import get_tracker, EvolutionTracker
    from api.storage_protocols import StorageProtocols
    from api.storage_vault import StorageVault
    vault = StorageVault(capacity=50)
    protocols = StorageProtocols(vault)
    tracker = EvolutionTracker(protocols)
    tracker.set_current_wave(405)
    tracker.record_module("wave_report_test", {"wave": 405}, "creation")
    report = tracker.get_wave_report(405)
    assert report["wave"] == 405
    assert report["module_count"] == 1
    assert report["modules"][0]["module_id"] == "wave_report_test"

def test_evolution_tracker_export():
    from api.evolution_tracker import get_tracker, EvolutionTracker
    from api.storage_protocols import StorageProtocols
    from api.storage_vault import StorageVault
    vault = StorageVault(capacity=50)
    protocols = StorageProtocols(vault)
    tracker = EvolutionTracker(protocols)
    tracker.set_current_wave(405)
    tracker.record_module("export_test", {"data": "test"}, "creation")
    export = tracker.export_evolution_log()
    assert export["tracker_version"] == "1.0"
    assert export["current_wave"] == 405
    assert export["total_modules"] >= 1
    assert "export_test" in export["modules"]


# ── Handler Tests ─────────────────────────────────────────────────

def test_storage_vault_handler():
    from api.storage_vault import handler
    # Status
    res = handler({"action": "status"}, {})
    assert res["status"] == "ok"
    assert "vault" in res
    # Store
    res = handler({"action": "store", "key": "handler_test", "value": {"x": 1}}, {})
    assert res["status"] == "stored"
    # Retrieve
    res = handler({"action": "retrieve", "key": "handler_test"}, {})
    assert res["status"] == "retrieved"
    assert res["value"] == {"x": 1}

def test_storage_protocols_handler():
    from api.storage_protocols import handler
    # Report
    res = handler({"action": "report"}, {})
    assert res["status"] == "ok"
    assert "report" in res
    # Store module
    res = handler({"action": "store_module", "module_id": "handler_mod", "data": {"handler": True}}, {})
    assert res["status"] == "stored"
    # Retrieve module
    res = handler({"action": "retrieve_module", "module_id": "handler_mod"}, {})
    assert res["status"] == "retrieved"
    assert res["data"] == {"handler": True}

def test_evolution_tracker_handler():
    from api.evolution_tracker import handler
    # Set wave
    res = handler({"action": "set_wave", "wave": 405}, {})
    assert res["status"] == "wave_set"
    assert res["current_wave"] == 405
    # Record
    res = handler({"action": "record", "module_id": "handler_evo", "data": {"handler": True}, "mutation_type": "test"}, {})
    assert res["status"] == "recorded"
    # History
    res = handler({"action": "history", "module_id": "handler_evo"}, {})
    assert res["status"] == "ok"
    assert res["history_length"] >= 1
    # Wave report
    res = handler({"action": "wave_report", "wave": 405}, {})
    assert res["status"] == "ok"
    assert "report" in res

print("All Wave 405 tests passed!")


# ── Social Ritual (Genesis Forge child) ───────────────────────────

def test_social_ritual_handler():
    from api.index import _call
    res = _call('GET', '/social-ritual?action=status')
    assert res["status"] == "active"
    assert res["module"] == "social_ritual"
    assert res["domain_family"] == "social"
    res = _call('POST', '/social-ritual?action=pulse', b'{}')
    assert res["module"] == "social_ritual"
    assert res["pulses"] >= 1

def test_social_ritual_coherence():
    from api.social_ritual import coherence_vitals, resonates_with
    vitals = coherence_vitals()
    assert "module_health" in vitals
    assert "resonance" in vitals
    assert "social_ritual_vitality" in vitals
    assert "genesis_era" in vitals
    assert resonates_with() == []

print("Social ritual tests passed!")
