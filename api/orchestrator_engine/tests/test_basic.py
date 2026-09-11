"""Basic tests for organism orchestrator."""

import sys
sys.path.insert(0, '.')

from src.orchestration.orchestrator import OrganismOrchestrator

def test_init():
    """Test orchestrator initialization."""
    o = OrganismOrchestrator()
    status = o.get_status()
    assert status["total_modules"] == 0
    assert status["total_waves"] == 0
    assert status["total_personas"] == 0
    assert status["organism_id"] == "organism_orchestrator"
    print("✓ Init test passed")

def test_module_lifecycle():
    """Test module registration and unregistration."""
    o = OrganismOrchestrator()
    o.register_module("m1", {"type": "test"})
    assert "m1" in o.modules
    assert o.get_status()["total_modules"] == 1
    
    o.unregister_module("m1")
    assert "m1" not in o.modules
    assert o.get_status()["total_modules"] == 0
    print("✓ Module lifecycle test passed")

def test_wave_evolution():
    """Test wave evolution."""
    o = OrganismOrchestrator()
    report = o.evolve_wave("w1", {"add_module": {"id": "m1", "type": "core"}})
    assert report["modules_after"] == 1
    assert report["coherence_after"] > report["coherence_before"]
    print("✓ Wave evolution test passed")

def test_persona_evolution():
    """Test persona evolution."""
    o = OrganismOrchestrator()
    persona = o.evolve_persona("agent_1", {"curiosity": 0.8})
    assert persona["curiosity"] == 0.8
    print("✓ Persona evolution test passed")

if __name__ == "__main__":
    test_init()
    test_module_lifecycle()
    test_wave_evolution()
    test_persona_evolution()
    print("All tests passed!")
