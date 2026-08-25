from __future__ import annotations
"""Cosmic Web Structure — maps large-scale codebase structure.

Like the cosmic web of galaxies connected by filaments, the codebase
forms a large-scale structure of modules connected by dependencies.
This maps that structure, identifying clusters (galaxies), filaments,
voids, and superclusters.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

@dataclass
class Galaxy:
    name: str
    modules: List[str]
    center_of_mass: float = 0.0
    total_mass: float = 0.0
    filament_connections: List[str] = field(default_factory=list)

@dataclass
class Filament:
    galaxies: List[str]
    thickness: float = 1.0
    length: float = 0.0

@dataclass
class Void:
    center: float
    radius: float
    density: float = 0.0

class CosmicWebMapper:
    def __init__(self):
        self.modules: Dict[str, float] = {}
        self.dependencies: Dict[str, Set[str]] = {}
        self.galaxies: Dict[str, Galaxy] = {}
        self.filaments: List[Filament] = []
        self.voids: List = []

    def add_module(self, name: str, mass: float = 1.0):
        self.modules[name] = mass
        self.dependencies.setdefault(name, set())

    def add_dependency(self, source: str, target: str):
        if source in self.modules and target in self.modules:
            self.dependencies[source].add(target)
            self.dependencies[target].add(source)

    def _cluster(self, threshold: float = 2.0) -> List[List[str]]:
        visited = set()
        clusters = []
        for name in self.modules:
            if name in visited:
                continue
            cluster = []
            stack = [name]
            while stack:
                n = stack.pop()
                if n in visited:
                    continue
                visited.add(n)
                cluster.append(n)
                for dep in self.dependencies.get(n, set()):
                    if dep not in visited:
                        stack.append(dep)
            if cluster:
                clusters.append(cluster)
        return clusters

    def map_web(self):
        clusters = self._cluster()
        for i, cluster in enumerate(clusters):
            total_mass = sum(self.modules.get(m, 1.0) for m in cluster)
            center = sum(i for i, m in enumerate(cluster)) / max(len(cluster), 1)
            galaxy = Galaxy(
                name=f"galaxy_{i}", modules=cluster,
                center_of_mass=center, total_mass=total_mass,
            )
            self.galaxies[galaxy.name] = galaxy

        galaxy_names = list(self.galaxies.keys())
        for i, g1 in enumerate(galaxy_names):
            for g2 in galaxy_names[i + 1:]:
                shared = set(self.galaxies[g1].modules) & set(self.galaxies[g2].modules)
                if shared:
                    filament = Filament(
                        galaxies=[g1, g2],
                        thickness=len(shared),
                        length=abs(self.galaxies[g1].center_of_mass -
                                  self.galaxies[g2].center_of_mass),
                    )
                    self.filaments.append(filament)
                    self.galaxies[g1].filament_connections.append(g2)
                    self.galaxies[g2].filament_connections.append(g1)

    def void_analysis(self) -> List[Dict]:
        galaxy_positions = sorted(
            [(g.center_of_mass, g.name) for g in self.galaxies.values()]
        )
        voids = []
        for i in range(len(galaxy_positions) - 1):
            gap = galaxy_positions[i + 1][0] - galaxy_positions[i][0]
            if gap > 3.0:
                voids.append({
                    "between": (galaxy_positions[i][1], galaxy_positions[i + 1][1]),
                    "gap_size": round(gap, 2),
                })
        return voids

    def summary(self) -> Dict:
        return {
            "modules": len(self.modules),
            "galaxies": len(self.galaxies),
            "filaments": len(self.filaments),
            "voids": len(self.void_analysis()),
            "largest_galaxy": max(
                self.galaxies.values(), key=lambda g: len(g.modules)
            ).name if self.galaxies else None,
            "total_mass": sum(self.modules.values()),
        }


def demo():
    mapper = CosmicWebMapper()
    print("=== Cosmic Web Structure Mapper ===")

    module_names = [
        "nucleus", "kernel", "agents", "sandbox", "protocols",
        "hex_vm", "pipeline", "observer", "meme_engine", "crystal",
        "photon", "dark_mapper", "tardigrade", "coral", "thermal",
    ]
    for i, name in enumerate(module_names):
        mapper.add_module(name, mass=i + 1)

    deps = [
        ("nucleus", "kernel"), ("nucleus", "agents"), ("nucleus", "sandbox"),
        ("agents", "observer"), ("sandbox", "hex_vm"), ("hex_vm", "pipeline"),
        ("pipeline", "crystal"), ("photon", "nucleus"), ("dark_mapper", "agents"),
        ("tardigrade", "sandbox"), ("coral", "thermal"), ("meme_engine", "observer"),
    ]
    for src, tgt in deps:
        mapper.add_dependency(src, tgt)

    mapper.map_web()
    summary = mapper.summary()
    print(f"  Modules: {summary['modules']}")
    print(f"  Galaxies: {summary['galaxies']}")
    print(f"  Filaments: {summary['filaments']}")
    print(f"  Voids: {summary['voids']}")
    print(f"  Largest galaxy: {summary['largest_galaxy']}")

    voids = mapper.void_analysis()
    if voids:
        print("\nVoids:")
        for v in voids:
            print(f"  Gap between {v['between']}: {v['gap_size']}")

    return summary


if __name__ == "__main__":
    demo()
