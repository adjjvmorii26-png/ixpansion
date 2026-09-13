"""Wave 446 — Quantum Coherence.

The organism explores quantum superposition of module states. Each module
can exist in multiple states simultaneously until observed. The organism
maintains a coherent quantum register where:

- Modules exist in superposition until measured
- Entanglement links module states across the organism
- Decoherence events collapse superpositions into classical states
- Quantum algorithms explore solution spaces exponentially

The organism computes in superposition.
"""
from __future__ import annotations
import json, time, random, math, hashlib
from pathlib import Path
from typing import Literal

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave446_quantum_coherence.json"


class QubitModule:
    """A module in quantum superposition."""

    def __init__(self, module_id: str, basis_states: list[str] = None):
        self.module_id = module_id
        self.basis_states = basis_states or ["ground", "excited", "metastable", "virtual"]
        self.amplitudes = {state: 1.0 / math.sqrt(len(self.basis_states)) for state in self.basis_states}
        self.phase = {state: 0.0 for state in self.basis_states}
        self.entangled_with: list[str] = []
        self.measured = False
        self.collapse_history: list[dict] = []

    def apply_hadamard(self) -> None:
        """Apply Hadamard gate - create superposition."""
        n = len(self.basis_states)
        new_amps = {}
        for i, state in enumerate(self.basis_states):
            new_amps[state] = sum(self.amplitudes[s] * (1 if i == j else -1) for j, s in enumerate(self.basis_states)) / math.sqrt(n)
        self.amplitudes = {k: v / math.sqrt(sum(abs(a)**2 for a in new_amps.values())) for k, v in new_amps.items()}

    def apply_phase(self, state: str, angle: float) -> None:
        """Apply phase rotation to a basis state."""
        if state in self.phase:
            self.phase[state] += angle

    def entangle(self, other_id: str) -> None:
        """Entangle with another module."""
        if other_id not in self.entangled_with:
            self.entangled_with.append(other_id)

    def measure(self) -> str:
        """Collapse superposition - return measured state."""
        probs = {s: abs(self.amplitudes[s])**2 for s in self.basis_states}
        total = sum(probs.values())
        probs = {s: p/total for s, p in probs.items()}
        r = random.random()
        cum = 0
        for state, prob in probs.items():
            cum += prob
            if r <= cum:
                self.measured = True
                self.collapse_history.append({"state": state, "timestamp": time.time()})
                return state
        return self.basis_states[0]

    def is_coherent(self) -> bool:
        """Check if still in superposition."""
        return not self.measured and len([s for s in self.basis_states if abs(self.amplitudes[s]) > 0.01]) > 1

    def decoherence_rate(self) -> float:
        """Rate of decoherence from environmental interaction."""
        entanglement_strength = len(self.entangled_with) * 0.1
        return max(0.01, 0.1 - entanglement_strength)

    def to_dict(self) -> dict:
        return {
            "module_id": self.module_id,
            "basis_states": self.basis_states,
            "probabilities": {s: round(abs(self.amplitudes[s])**2, 4) for s in self.basis_states},
            "phases": {s: round(self.phase[s], 4) for s in self.basis_states},
            "entangled_with": self.entangled_with,
            "measured": self.measured,
            "coherent": self.is_coherent(),
            "decoherence_rate": round(self.decoherence_rate(), 6),
        }


class QuantumRegister:
    """The organism's quantum register."""

    def __init__(self):
        self.qubits: dict[str, QubitModule] = {}
        self.total_coherence = 1.0
        self.decoherence_events = 0
        self.measurement_count = 0

    def add_qubit(self, module_id: str, basis_states: list[str] = None) -> QubitModule:
        qb = QubitModule(module_id, basis_states)
        self.qubits[module_id] = qb
        return qb

    def entangle(self, module_a: str, module_b: str) -> bool:
        """Create entanglement between two modules."""
        if module_a in self.qubits and module_b in self.qubits:
            self.qubits[module_a].entangle(module_b)
            self.qubits[module_b].entangle(module_a)
            return True
        return False

    def apply_global_hadamard(self) -> int:
        """Put all coherent qubits into superposition."""
        count = 0
        for qb in self.qubits.values():
            if qb.is_coherent():
                qb.apply_hadamard()
                count += 1
        return count

    def measure_all(self) -> dict[str, str]:
        """Measure all qubits."""
        results = {}
        for mod_id, qb in self.qubits.items():
            if not qb.measured:
                results[mod_id] = qb.measure()
                self.measurement_count += 1
        return results

    def evolve(self, time_step: float = 1.0) -> dict:
        """Evolve the register under decoherence."""
        decohered = 0
        for qb in self.qubits.values():
            if qb.is_coherent():
                if random.random() < qb.decoherence_rate() * time_step:
                    qb.measure()
                    decohered += 1
                    self.decoherence_events += 1
        return {"decohered": decohered, "remaining_coherent": sum(1 for q in self.qubits.values() if q.is_coherent())}

    def get_register_state(self) -> dict:
        coherent = sum(1 for q in self.qubits.values() if q.is_coherent())
        return {
            "total_qubits": len(self.qubits),
            "coherent": coherent,
            "measured": sum(1 for q in self.qubits.values() if q.measured),
            "total_coherence": round(self.total_coherence, 4),
            "decoherence_events": self.decoherence_events,
            "measurement_count": self.measurement_count,
            "qubits": {m: q.to_dict() for m, q in self.qubits.items()},
        }


def coherence_vitals() -> dict:
    return {"organ": "wave446_quantum_coherence", "wave": 446, "status": "active"}


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"qubits": {}, "decoherence_events": 0, "measurement_count": 0}


def _save(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    reg = QuantumRegister()

    for mod_id, q_data in state.get("qubits", {}).items():
        qb = QubitModule(mod_id, q_data.get("basis_states"))
        qb.amplitudes = {s: math.sqrt(p) for s, p in q_data.get("probabilities", {}).items()}
        qb.phase = q_data.get("phases", {})
        qb.entangled_with = q_data.get("entangled_with", [])
        qb.measured = q_data.get("measured", False)
        reg.qubits[mod_id] = qb

    reg.decoherence_events = state.get("decoherence_events", 0)
    reg.measurement_count = state.get("measurement_count", 0)

    if action == "status":
        return {"action": "status", "wave": 446, **reg.get_register_state()}

    elif action == "add_qubit":
        module_id = req.get("module_id", f"qubit_{int(time.time())}")
        basis = req.get("basis_states", ["ground", "excited", "metastable", "virtual"])
        qb = reg.add_qubit(module_id, basis)
        state["qubits"][module_id] = qb.to_dict()
        _save(state)
        return {"action": "add_qubit", "qubit": qb.to_dict()}

    elif action == "entangle":
        a = req.get("module_a", "")
        b = req.get("module_b", "")
        if reg.entangle(a, b):
            state["qubits"] = {m: q.to_dict() for m, q in reg.qubits.items()}
            _save(state)
            return {"action": "entangle", "entangled": True, "pair": [a, b]}
        return {"error": "modules not found"}

    elif action == "hadamard":
        count = reg.apply_global_hadamard()
        state["qubits"] = {m: q.to_dict() for m, q in reg.qubits.items()}
        _save(state)
        return {"action": "hadamard", "qubits_put_in_superposition": count}

    elif action == "measure":
        module_id = req.get("module_id")
        if module_id and module_id in reg.qubits:
            result = reg.qubits[module_id].measure()
            state["qubits"] = {m: q.to_dict() for m, q in reg.qubits.items()}
            _save(state)
            return {"action": "measure", "module": module_id, "result": result}
        else:
            results = reg.measure_all()
            state["qubits"] = {m: q.to_dict() for m, q in reg.qubits.items()}
            _save(state)
            return {"action": "measure_all", "results": results}

    elif action == "evolve":
        result = reg.evolve(req.get("time_step", 1.0))
        state["qubits"] = {m: q.to_dict() for m, q in reg.qubits.items()}
        state["decoherence_events"] = reg.decoherence_events
        _save(state)
        return {"action": "evolve", **result}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    req = {"action": action}
    result = handler(req)
    print(json.dumps(result, indent=2, default=str))
