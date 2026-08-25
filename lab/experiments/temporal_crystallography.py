"""Temporal Crystallography — Maps wave evolution as crystal lattice structures.

Each wave of development is treated as a crystal plane. The module computes
lattice vectors, symmetry groups, and defect patterns across the evolution
history, revealing the "crystal structure" of the codebase's growth.
"""
from __future__ import annotations
import hashlib
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class CrystalLattice:
    """Represents the evolutionary crystal structure of a codebase."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.planes = []
        self.defects = []

    def measure_wave_plane(self, wave_num: int, modules: list[str], lines: int) -> dict:
        """Treat a wave as a crystal plane with measurable properties."""
        # Lattice parameter: density of modules per unit
        density = len(modules) / max(1, lines / 100)

        # Symmetry: how many modules share naming conventions
        prefixes = {}
        for m in modules:
            parts = m.split("_")
            if parts:
                prefixes[parts[0]] = prefixes.get(parts[0], 0) + 1
        symmetry_order = max(prefixes.values()) if prefixes else 1

        # Miller indices: represent the plane orientation
        h = wave_num % 3 + 1
        k = (wave_num // 3) % 3 + 1
        l = (wave_num // 9) % 3 + 1

        # Interplanar spacing (analogous to d-spacing in crystallography)
        d_spacing = 1.0 / max(0.01, (h**2 + k**2 + l**2) ** 0.5)

        plane = {
            "wave": wave_num,
            "modules": modules,
            "module_count": len(modules),
            "total_lines": lines,
            "density": round(density, 4),
            "symmetry_order": symmetry_order,
            "miller_indices": (h, k, l),
            "d_spacing": round(d_spacing, 4),
            "hash": hashlib.md5(str(modules).encode()).hexdigest()[:8],
        }
        self.planes.append(plane)
        return plane

    def detect_defects(self) -> list[dict]:
        """Find structural defects (anomalies) in the crystal."""
        for i in range(len(self.planes) - 1):
            curr = self.planes[i]
            nxt = self.planes[i + 1]

            # Vacancy defect: wave with significantly fewer modules
            if nxt["module_count"] < curr["module_count"] * 0.5:
                self.defects.append({
                    "type": "vacancy",
                    "between_waves": (curr["wave"], nxt["wave"]),
                    "severity": "high",
                    "detail": f"Module count dropped from {curr['module_count']} to {nxt['module_count']}",
                })

            # Interstitial defect: sudden density spike
            if nxt["density"] > curr["density"] * 2:
                self.defects.append({
                    "type": "interstitial",
                    "between_waves": (curr["wave"], nxt["wave"]),
                    "severity": "medium",
                    "detail": f"Density spiked from {curr['density']:.3f} to {nxt['density']:.3f}",
                })

            # Dislocation: symmetry change
            if abs(nxt["symmetry_order"] - curr["symmetry_order"]) > 3:
                self.defects.append({
                    "type": "dislocation",
                    "between_waves": (curr["wave"], nxt["wave"]),
                    "severity": "low",
                    "detail": f"Symmetry order shifted from {curr['symmetry_order']} to {nxt['symmetry_order']}",
                })

        return self.defects

    def compute_lattice_energy(self) -> float:
        """Compute total lattice energy (stability metric)."""
        if not self.planes:
            return 0.0

        energy = 0.0
        for plane in self.planes:
            # Energy from density and symmetry
            energy += plane["density"] * plane["symmetry_order"]
            # Energy from d-spacing (more spacing = more stable)
            energy += plane["d_spacing"] * 10

        # Penalty for defects
        energy -= len(self.defects) * 5.0

        return round(energy, 4)

    def classify_structure(self) -> str:
        """Classify the overall crystal structure type."""
        n = len(self.planes)
        if n == 0:
            return "amorphous"
        elif n <= 3:
            return "primitive_cubic"
        elif n <= 7:
            return "body_centered"
        elif n <= 12:
            return "face_centered"
        else:
            return "complex_hexagonal"

    def report(self) -> dict:
        """Generate the full crystallography report."""
        self.detect_defects()
        energy = self.compute_lattice_energy()
        structure = self.classify_structure()

        return {
            "crystal": "temporal_crystallography",
            "planes": len(self.planes),
            "structure_type": structure,
            "lattice_energy": energy,
            "defects": self.defects,
            "defect_count": len(self.defects),
            "plane_details": self.planes,
        }


def demo():
    import random
    rng = random.Random(42)
    lattice = CrystalLattice(seed=42)

    # Simulate 8 waves of evolution
    wave_modules = {
        72: (["spectral_drift", "temporal_resonance", "paradox_breeding",
               "neural_topology", "cross_pollinator", "consciousness_fingerprint",
               "memory_palace", "causal_causeway"], 2800),
        73: (["dream_terrain_crystallizer", "morphic_resonance_lattice",
               "temporal_debt_auditor", "attention_economy_sim",
               "ghost_protocol_weaver", "reality_bleed_detector",
               "dimensional_portal_network"], 2400),
        74: (["mood_synesthesia", "negative_space_cartographer",
               "pulse_harmonics_analyzer", "cordyceps_mutation_engine",
               "constellation_narrative", "proof_density_analyzer"], 2100),
        75: (["consensus_reality_sim", "panopticon_ecology",
               "hex_vm_profiler", "expansion_rule_synth",
               "glitch_pattern_generator", "chrono_forge_orchestrator"], 2200),
        76: (["reactor_fusion_sim", "quantum_tunneling_sim",
               "hyphal_decision_engine", "dialect_evolution",
               "reality_fabric_sim", "chronicle_engine_sim"], 2000),
        77: (["evolution_kernel", "fractal_reactor_grid",
               "mycelial_governor", "omega_prime_dreamforge",
               "constellation_autobiographer", "paradox_singularity_monitor"], 1900),
        78: (["websocket_reactor", "live_experiment_runner"], 1200),
        79: (["vercel_echo_chamber", "temporal_crystallography",
               "quantum_coherence_map", "neural_sedimentology",
               "sentient_dashboard", "dream_synthesis_v2"], 1800),
    }

    for wave_num, (modules, lines) in wave_modules.items():
        lattice.measure_wave_plane(wave_num, modules, lines)

    return lattice.report()


def main():
    import json as _json
    result = demo()
    print(_json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
