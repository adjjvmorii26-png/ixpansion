"""Neural Sedimentology — Models accumulated decisions as geological strata.

Each layer of the codebase is treated as a geological stratum. The module
computes sediment density, erosion patterns, fossil records (dead code),
and tectonic pressure (refactoring hotspots) to create a geological
cross-section of the repository's history.
"""
from __future__ import annotations
import hashlib
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Stratum:
    """A single geological layer in the codebase."""

    def __init__(self, name: str, age: int, files: list[str], total_lines: int):
        self.name = name
        self.age = age  # Older = higher number
        self.files = files
        self.total_lines = total_lines

        # Geological properties
        self.density = total_lines / max(1, len(files))  # Lines per file
        self.fossil_count = 0  # Dead code artifacts
        self.erosion_index = 0.0  # How much has been modified
        self.composition = self._compute_composition()

    def _compute_composition(self) -> dict:
        """Analyze the composition of this stratum."""
        # Categorize files by naming patterns
        categories = {"core": 0, "test": 0, "config": 0, "interface": 0, "data": 0}
        for f in self.files:
            lower = f.lower()
            if "test" in lower:
                categories["test"] += 1
            elif "config" in lower or "yaml" in lower or "json" in lower:
                categories["config"] += 1
            elif any(w in lower for w in ["cli", "api", "dashboard", "ui", "adapter"]):
                categories["interface"] += 1
            elif any(w in lower for w in ["data", "vault", "log", "archive"]):
                categories["data"] += 1
            else:
                categories["core"] += 1
        return categories

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "age": self.age,
            "file_count": len(self.files),
            "total_lines": self.total_lines,
            "density": round(self.density, 2),
            "fossil_count": self.fossil_count,
            "erosion_index": round(self.erosion_index, 4),
            "composition": self.composition,
        }


class Sedimentology:
    """Geological analysis of the codebase."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.strata = []
        self.tectonic_events = []

    def add_stratum(self, name: str, age: int, files: list[str], total_lines: int):
        """Add a geological layer."""
        stratum = Stratum(name, age, files, total_lines)
        self.strata.append(stratum)
        return stratum

    def detect_fossils(self, stratum: Stratum) -> list[str]:
        """Find dead code artifacts (fossils) in a stratum."""
        fossils = []
        for fname in stratum.files:
            # Heuristic: files with very few functions might be stubs
            if any(pattern in fname for pattern in ["_old", "_backup", "_unused", "_deprecated"]):
                fossils.append(fname)
        stratum.fossil_count = len(fossils)
        return fossils

    def compute_erosion(self):
        """Measure how much each stratum has been eroded (modified over time)."""
        for stratum in self.strata:
            # Erosion based on density variance from average
            avg_density = sum(s.density for s in self.strata) / max(1, len(self.strata))
            if avg_density > 0:
                stratum.erosion_index = abs(stratum.density - avg_density) / avg_density

    def detect_tectonic_events(self):
        """Find major structural shifts (tectonic events)."""
        for i in range(len(self.strata) - 1):
            curr = self.strata[i]
            nxt = self.strata[i + 1]

            # Density jump = tectonic shift
            if curr.density > 0 and nxt.density > 0:
                ratio = nxt.density / curr.density
                if ratio > 2.0 or ratio < 0.5:
                    self.tectonic_events.append({
                        "type": "density_shift",
                        "between": (curr.name, nxt.name),
                        "ratio": round(ratio, 3),
                        "severity": "major" if ratio > 3.0 or ratio < 0.33 else "minor",
                    })

            # Composition change
            curr_core = curr.composition.get("core", 0)
            nxt_core = nxt.composition.get("core", 0)
            if curr_core > 0 and nxt_core > 0:
                comp_ratio = nxt_core / curr_core
                if comp_ratio > 2.0 or comp_ratio < 0.5:
                    self.tectonic_events.append({
                        "type": "composition_shift",
                        "between": (curr.name, nxt.name),
                        "ratio": round(comp_ratio, 3),
                        "severity": "minor",
                    })

    def cross_section(self) -> list[dict]:
        """Generate a geological cross-section."""
        self.compute_erosion()
        self.detect_tectonic_events()

        # Find fossils in each layer
        for stratum in self.strata:
            self.detect_fossils(stratum)

        return [s.to_dict() for s in self.strata]

    def report(self) -> dict:
        """Generate full sedimentology report."""
        cross_section = self.cross_section()

        total_fossils = sum(s.fossil_count for s in self.strata)
        total_lines = sum(s.total_lines for s in self.strata)
        avg_erosion = (
            sum(s.erosion_index for s in self.strata) / max(1, len(self.strata))
        )

        # Classify the geological era
        n = len(self.strata)
        if n <= 3:
            era = "precambrian"
        elif n <= 6:
            era = "paleozoic"
        elif n <= 10:
            era = "mesozoic"
        else:
            era = "cenozoic"

        return {
            "geology": "neural_sedimentology",
            "era": era,
            "strata_count": n,
            "total_lines": total_lines,
            "total_fossils": total_fossils,
            "avg_erosion": round(avg_erosion, 4),
            "tectonic_events": self.tectonic_events,
            "tectonic_event_count": len(self.tectonic_events),
            "cross_section": cross_section,
            "verdict": (
                f"Codebase spans {n} geological strata ({era} era) "
                f"with {total_fossils} fossil artifacts and "
                f"{len(self.tectonic_events)} tectonic events."
            ),
        }


def demo():
    geo = Sedimentology(seed=42)

    # Map the repo's subsystems as geological strata (oldest first)
    layer_data = [
        ("project_root_core", 8, ["runtime.py", "state_graph.py", "registry.py", "events.py", "config_loader.py"], 800),
        ("omega_prime_base", 7, ["agent_base.py", "reactor.py", "pulse_loop.py", "state_core.py", "conductor.py"], 1200),
        ("ixpansion_kernel", 6, ["base.py", "architect.py", "mutator.py", "observer.py", "vm.py"], 1500),
        ("bridges_layer", 5, ["bridge_core.py", "resonance_loom.py", "counterfactual_twin.py", "divergence_forensics.py"], 1800),
        ("lab_experiments", 4, ["spectral_drift.py", "temporal_resonance.py", "paradox_breeding.py"], 2000),
        ("mycelium_network", 3, ["__init__.py", "README.md"], 300),
        ("constellation_map", 2, ["engine.py", "loom.py", "recovery.py", "treaties.py", "atlas.py"], 1600),
        ("vercel_api", 1, ["health.py", "telemetry.py", "experiments.py", "agents.py", "sandbox.py"], 900),
    ]

    for name, age, files, lines in layer_data:
        geo.add_stratum(name, age, files, lines)

    return geo.report()


def main():
    import json as _json
    result = demo()
    print(_json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
