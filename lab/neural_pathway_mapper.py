"""Neural Pathway Mapper — Traces execution paths as neural pathways.

Maps how code flows through the system, creating a "brain scan" of
the repository that reveals which paths are most traveled and which
are dormant.
"""
from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Pathway:
    def __init__(self, source: str, target: str, weight: float = 1.0):
        self.source = source
        self.target = target
        self.weight = weight
        self.activations = 0

    def activate(self):
        self.weight = min(10.0, self.weight + 0.1)
        self.activations += 1

    def to_dict(self) -> dict:
        return {"source": self.source, "target": self.target,
                "weight": round(self.weight, 2), "activations": self.activations}


class NeuralPathwayMapper:
    def __init__(self, seed=42):
        self.seed = seed
        self.pathways: dict[tuple[str, str], Pathway] = {}
        self.regions: dict[str, dict] = {}
        self.scan_count = 0

    def scan_region(self, name: str, base: Path):
        if not base.exists():
            return
        modules = []
        for py in base.glob("*.py"):
            if py.name.startswith("_") or py.name.startswith("test_"):
                continue
            text = py.read_text(errors="replace")
            lines = text.splitlines()
            funcs = [l.strip().split("(")[0].replace("def ", "") for l in lines if l.strip().startswith("def ")]
            modules.append({"name": py.stem, "functions": funcs, "lines": len(lines)})
        self.regions[name] = modules
        self.scan_count += 1

        # Create pathways between modules with similar function names
        for i, a in enumerate(modules):
            for b in modules[i+1:]:
                overlap = len(set(a["functions"]) & set(b["functions"]))
                if overlap > 0:
                    key = (a["name"], b["name"])
                    if key not in self.pathways:
                        self.pathways[key] = Pathway(a["name"], b["name"], overlap)
                    else:
                        self.pathways[key].activate()

    def simulate_activation(self, start: str, hops: int = 3) -> list[str]:
        path = [start]
        current = start
        for _ in range(hops):
            candidates = [(p.target, p.weight) for p in self.pathways.values() if p.source == current]
            if not candidates:
                break
            candidates.sort(key=lambda x: x[1], reverse=True)
            current = candidates[0][0]
            path.append(current)
        return path

    def find_highways(self, min_weight: float = 2.0) -> list[dict]:
        highways = [p.to_dict() for p in self.pathways.values() if p.weight >= min_weight]
        highways.sort(key=lambda x: x["weight"], reverse=True)
        return highways[:10]

    def brain_scan(self) -> dict:
        total_pathways = len(self.pathways)
        total_weight = sum(p.weight for p in self.pathways.values())
        avg_weight = total_weight / max(1, total_pathways)
        highways = self.find_highways()
        return {
            "scan_count": self.scan_count,
            "regions": {name: len(mods) for name, mods in self.regions.items()},
            "total_pathways": total_pathways,
            "avg_weight": round(avg_weight, 4),
            "highways": highways,
        }

    def report(self) -> dict:
        scan = self.brain_scan()
        return {"mapper": "neural_pathway_mapper", **scan}


def demo():
    mapper = NeuralPathwayMapper(seed=42)
    mapper.scan_region("api", ROOT / "api")
    mapper.scan_region("lab", ROOT / "lab" / "experiments")
    mapper.scan_region("bridges", ROOT / "bridges")
    return mapper.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
