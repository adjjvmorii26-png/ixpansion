"""Quantum Coherence Map — Models module interdependencies as quantum states.

Each module is a qubit with a coherence score. Entanglement represents
tight coupling. Decoherence represents drift. The map computes the
quantum state of the entire codebase.
"""
from __future__ import annotations
import hashlib
import math
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Qubit:
    """Represents a module as a quantum qubit."""

    def __init__(self, name: str, subsystem: str, size: int, import_count: int):
        self.name = name
        self.subsystem = subsystem
        self.size = size
        self.import_count = import_count

        # Quantum properties
        self.coherence = min(1.0, import_count / 10.0)  # More imports = more coherent
        self.phase = (hash(name) % 360) * math.pi / 180  # Unique phase
        self.amplitude = min(1.0, size / 500.0)  # Larger = higher amplitude
        self.entangled_with = []

    def state_vector(self) -> tuple[float, float]:
        """Returns (alpha, beta) of the qubit state |ψ⟩ = α|0⟩ + β|1⟩."""
        alpha = self.amplitude * math.cos(self.phase)
        beta = self.amplitude * math.sin(self.phase)
        return (round(alpha, 6), round(beta, 6))

    def fidelity(self) -> float:
        """Fidelity: how well-defined the state is."""
        alpha, beta = self.state_vector()
        return round(alpha**2 + beta**2, 6)

    def entropy(self) -> float:
        """Von Neumann entropy of the qubit."""
        f = self.fidelity()
        if f <= 0 or f >= 1:
            return 0.0
        return round(-f * math.log2(f) - (1 - f) * math.log2(1 - f), 6)


class CoherenceMap:
    """Quantum coherence map of the entire codebase."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.qubits = {}
        self.entanglements = []
        self.measurement_results = []

    def register_module(self, name: str, subsystem: str, size: int, import_count: int):
        """Register a module as a qubit."""
        self.qubits[name] = Qubit(name, subsystem, size, import_count)

    def compute_entanglement(self, name_a: str, name_b: str) -> float:
        """Compute entanglement between two modules based on import overlap."""
        if name_a not in self.qubits or name_b not in self.qubits:
            return 0.0

        qa = self.qubits[name_a]
        qb = self.qubits[name_b]

        # Bell state correlation: more shared imports = higher entanglement
        shared = min(qa.import_count, qb.import_count)
        total = qa.import_count + qb.import_count
        entanglement = shared / max(1, total) * 2  # Normalized to [0, 1]

        self.entanglements.append({
            "pair": (name_a, name_b),
            "entanglement": round(entanglement, 6),
            "bell_state": "Φ+" if entanglement > 0.5 else "Ψ+" if entanglement > 0.3 else "Ψ-",
        })

        qa.entangled_with.append(name_b)
        qb.entangled_with.append(name_a)

        return round(entanglement, 6)

    def measure_all(self) -> dict:
        """Simulate measurement on all qubits."""
        results = []
        for name, qubit in self.qubits.items():
            fidelity = qubit.fidelity()
            entropy = qubit.entropy()
            alpha, beta = qubit.state_vector()

            # Measurement collapses to |0⟩ or |1⟩
            import random
            rng = random.Random(hash(name) + self.seed)
            outcome = "0" if rng.random() < alpha**2 else "1"

            results.append({
                "qubit": name,
                "subsystem": qubit.subsystem,
                "outcome": outcome,
                "fidelity": fidelity,
                "entropy": entropy,
                "state": {"alpha": alpha, "beta": beta},
                "entanglement_count": len(qubit.entangled_with),
            })

        self.measurement_results = results
        return results

    def compute_coherence_score(self) -> float:
        """Overall quantum coherence of the system."""
        if not self.qubits:
            return 0.0

        fidelities = [q.fidelity() for q in self.qubits.values()]
        avg_fidelity = sum(fidelities) / len(fidelities)

        entanglement_density = (
            len(self.entanglements) / max(1, len(self.qubits) * (len(self.qubits) - 1) / 2)
        )

        # Coherence = average fidelity weighted by entanglement density
        coherence = avg_fidelity * (0.7 + 0.3 * entanglement_density)
        return round(coherence, 6)

    def report(self) -> dict:
        """Generate full quantum coherence report."""
        # Auto-compute entanglements for top-20 most connected modules
        sorted_qubits = sorted(
            self.qubits.values(), key=lambda q: q.import_count, reverse=True
        )[:20]

        for i, qa in enumerate(sorted_qubits):
            for qb in sorted_qubits[i+1:]:
                if qa.subsystem == qb.subsystem or qa.import_count > 3:
                    self.compute_entanglement(qa.name, qb.name)

        measurements = self.measure_all()
        coherence = self.compute_coherence_score()

        # Group by subsystem
        subsystem_states = {}
        for m in measurements:
            s = m["subsystem"]
            if s not in subsystem_states:
                subsystem_states[s] = {"qubits": 0, "avg_fidelity": 0.0, "total_entropy": 0.0}
            subsystem_states[s]["qubits"] += 1
            subsystem_states[s]["avg_fidelity"] += m["fidelity"]
            subsystem_states[s]["total_entropy"] += m["entropy"]

        for s in subsystem_states:
            n = subsystem_states[s]["qubits"]
            subsystem_states[s]["avg_fidelity"] = round(subsystem_states[s]["avg_fidelity"] / max(1, n), 6)
            subsystem_states[s]["total_entropy"] = round(subsystem_states[s]["total_entropy"], 6)

        return {
            "quantum_map": "quantum_coherence_map",
            "qubit_count": len(self.qubits),
            "entanglement_count": len(self.entanglements),
            "coherence_score": coherence,
            "subsystem_states": subsystem_states,
            "measurements": measurements[:30],
            "top_entanglements": sorted(
                self.entanglements, key=lambda e: e["entanglement"], reverse=True
            )[:10],
        }


def demo():
    cmap = CoherenceMap(seed=42)

    # Register key modules from the codebase
    api_dir = ROOT / "api"
    lab_dir = ROOT / "lab" / "experiments"

    for d, subsys in [(api_dir, "api"), (lab_dir, "lab")]:
        if d.exists():
            for py in d.glob("*.py"):
                if py.name.startswith("_"):
                    continue
                text = py.read_text(errors="replace")
                import_count = sum(
                    1 for ln in text.splitlines()
                    if ln.strip().startswith(("import ", "from "))
                )
                cmap.register_module(
                    py.stem, subsys, py.stat().st_size, import_count
                )

    # Register bridge modules
    bridge_dir = ROOT / "bridges"
    if bridge_dir.exists():
        for py in bridge_dir.glob("*.py"):
            if py.name.startswith("_") or py.name.startswith("test_"):
                continue
            text = py.read_text(errors="replace")
            import_count = sum(
                1 for ln in text.splitlines()
                if ln.strip().startswith(("import ", "from "))
            )
            cmap.register_module(py.stem, "bridges", py.stat().st_size, import_count)

    return cmap.report()


def main():
    import json as _json
    result = demo()
    print(_json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
