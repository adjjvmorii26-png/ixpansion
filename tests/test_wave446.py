"""Tests for Wave 446 — Quantum Coherence."""
import pytest
from api.wave446_quantum_coherence import QubitModule, QuantumRegister, handler, coherence_vitals

def test_coherence_vitals():
    v = coherence_vitals()
    assert v["organ"] == "wave446_quantum_coherence"
    assert v["wave"] == 446

def test_qubit_init():
    qb = QubitModule("q1")
    assert qb.module_id == "q1"
    assert len(qb.basis_states) == 4
    assert not qb.measured

def test_qubit_hadamard():
    qb = QubitModule("q1")
    qb.apply_hadamard()
    # Hadamard creates superposition
    probs = sum(abs(qb.amplitudes[s])**2 for s in qb.basis_states)
    assert abs(probs - 1.0) < 0.01

def test_qubit_measure():
    qb = QubitModule("q1")
    qb.amplitudes = {"ground": 1.0, "excited": 0.0, "metastable": 0.0, "virtual": 0.0}
    result = qb.measure()
    assert result == "ground"
    assert qb.measured

def test_qubit_entangle():
    qb1 = QubitModule("q1")
    qb2 = QubitModule("q2")
    qb1.entangle("q2")
    assert "q2" in qb1.entangled_with

def test_register_init():
    reg = QuantumRegister()
    assert len(reg.qubits) == 0

def test_add_qubit():
    reg = QuantumRegister()
    qb = reg.add_qubit("q1")
    assert "q1" in reg.qubits

def test_entangle():
    reg = QuantumRegister()
    reg.add_qubit("q1")
    reg.add_qubit("q2")
    assert reg.entangle("q1", "q2")
    assert "q2" in reg.qubits["q1"].entangled_with

def test_hadamard():
    reg = QuantumRegister()
    reg.add_qubit("q1")
    reg.add_qubit("q2")
    count = reg.apply_global_hadamard()
    assert count == 2

def test_measure():
    reg = QuantumRegister()
    reg.add_qubit("q1")
    reg.add_qubit("q2")
    reg.qubits["q1"].amplitudes = {"ground": 1.0, "excited": 0.0, "metastable": 0.0, "virtual": 0.0}
    result = reg.measure_all()
    assert "q1" in result

def test_evolve():
    reg = QuantumRegister()
    qb = reg.add_qubit("q1")
    # Force decoherence
    qb.decoherence_rate = lambda: 1.0
    result = reg.evolve(1.0)
    assert "decohered" in result

def test_handler_status():
    result = handler({"action": "status"})
    assert result["action"] == "status"
    assert result["wave"] == 446

def test_handler_add_qubit():
    result = handler({"action": "add_qubit", "module_id": "test"})
    assert result["action"] == "add_qubit"

def test_handler_entangle():
    handler({"action": "add_qubit", "module_id": "a"})
    handler({"action": "add_qubit", "module_id": "b"})
    result = handler({"action": "entangle", "module_a": "a", "module_b": "b"})
    assert result["action"] == "entangle"

def test_handler_hadamard():
    result = handler({"action": "hadamard"})
    assert result["action"] == "hadamard"

def test_handler_measure():
    handler({"action": "add_qubit", "module_id": "m1"})
    result = handler({"action": "measure", "module_id": "m1"})
    assert result["action"] == "measure"

def test_handler_evolve():
    result = handler({"action": "evolve"})
    assert result["action"] == "evolve"

def test_handler_unknown():
    result = handler({"action": "unknown"})
    assert "error" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
