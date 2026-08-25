from __future__ import annotations
"""Crystalline Lattice — perfect ordered structure generation.

Generates crystal lattices from seed patterns using symmetry operations.
Each crystal has a unique signature based on its growth rules. Lattices
can be compared for similarity, and "defects" can be introduced for stress.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

@dataclass
class LatticeNode:
    x: float
    y: float
    z: float
    element: str = "Si"
    bonds: List[Tuple[int, int, int]] = field(default_factory=list)
    defect: bool = False
    energy: float = 0.0

@dataclass
class Crystal:
    name: str
    nodes: List[LatticeNode] = field(default_factory=list)
    symmetry: str = "cubic"
    unit_cell_size: float = 1.0
    generation: int = 0
    defect_count: int = 0

    def signature(self) -> str:
        coords = [(round(n.x, 2), round(n.y, 2), round(n.z, 2), n.element) for n in self.nodes]
        raw = json.dumps(coords, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def volume(self) -> float:
        if not self.nodes:
            return 0.0
        xs = [n.x for n in self.nodes]
        ys = [n.y for n in self.nodes]
        zs = [n.z for n in self.nodes]
        return (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1) * (max(zs) - min(zs) + 1)

    def density(self) -> float:
        v = self.volume()
        return len(self.nodes) / max(v, 1.0)


class CrystallineLatticeEngine:
    ELEMENTS = ["Si", "C", "Ge", "B", "N", "P", "As", "Ga"]

    def __init__(self):
        self.crystals: Dict[str, Crystal] = {}
        self.growth_log: List[Dict] = []

    def _seed_hash(self, seed: str) -> List[int]:
        h = hashlib.sha256(seed.encode()).digest()
        return list(h)

    def grow(self, name: str, seed: str, layers: int = 3,
             symmetry: str = "cubic") -> Crystal:
        crystal = Crystal(name=name, symmetry=symmetry)
        seed_bytes = self._seed_hash(seed)
        lattice_spacing = 1.0

        if symmetry == "cubic":
            offsets = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1),
                       (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1)]
        elif symmetry == "hexagonal":
            offsets = [(0, 0, 0), (1, 0, 0), (0.5, 0.866, 0),
                       (1.5, 0.866, 0), (0, 0, 1), (1, 0, 1),
                       (0.5, 0.866, 1), (1.5, 0.866, 1)]
        else:
            offsets = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]

        node_idx = 0
        for layer in range(layers):
            for dx, dy, dz in offsets:
                element = self.ELEMENTS[seed_bytes[node_idx % len(seed_bytes)] % len(self.ELEMENTS)]
                x = dx * lattice_spacing + layer * lattice_spacing
                y = dy * lattice_spacing
                z = dz * lattice_spacing
                node = LatticeNode(x=x, y=y, z=z, element=element)
                crystal.nodes.append(node)
                node_idx += 1

        for i, node in enumerate(crystal.nodes):
            for j, other in enumerate(crystal.nodes):
                if i >= j:
                    continue
                dist = math.sqrt(
                    (node.x - other.x) ** 2 +
                    (node.y - other.y) ** 2 +
                    (node.z - other.z) ** 2
                )
                if dist <= lattice_spacing * 1.5:
                    node.bonds.append((int(other.x), int(other.y), int(other.z)))
                    other.bonds.append((int(node.x), int(node.y), int(node.z)))

        crystal.generation = layers
        self.crystals[name] = crystal
        self.growth_log.append({
            "name": name, "seed": seed, "layers": layers,
            "symmetry": symmetry, "nodes": len(crystal.nodes),
            "signature": crystal.signature(),
        })
        return crystal

    def introduce_defects(self, crystal_name: str, count: int = 1,
                          seed: int = 42) -> int:
        if crystal_name not in self.crystals:
            return 0
        rng = __import__("random").Random(seed)
        crystal = self.crystals[crystal_name]
        introduced = 0
        for node in crystal.nodes:
            if introduced >= count:
                break
            if not node.defect and rng.random() < 0.3:
                node.defect = True
                node.element = "V"  # Vacancy
                node.energy = -2.5
                introduced += 1
        crystal.defect_count = sum(1 for n in crystal.nodes if n.defect)
        return introduced

    def compare(self, a: str, b: str) -> Dict:
        if a not in self.crystals or b not in self.crystals:
            return {"error": "crystal not found"}
        ca, cb = self.crystals[a], self.crystals[b]
        elements_a = [n.element for n in ca.nodes]
        elements_b = [n.element for n in cb.nodes]
        shared = set(elements_a) & set(elements_b)
        return {
            "a_nodes": len(ca.nodes), "b_nodes": len(cb.nodes),
            "a_volume": round(ca.volume(), 2), "b_volume": round(cb.volume(), 2),
            "a_density": round(ca.density(), 4), "b_density": round(cb.density(), 4),
            "shared_elements": list(shared),
            "a_defects": ca.defect_count, "b_defects": cb.defect_count,
            "a_signature": ca.signature(), "b_signature": cb.signature(),
        }

    def lattice_info(self, name: str) -> Dict:
        if name not in self.crystals:
            return {"error": "not found"}
        c = self.crystals[name]
        return {
            "name": c.name, "symmetry": c.symmetry,
            "nodes": len(c.nodes), "volume": round(c.volume(), 2),
            "density": round(c.density(), 4), "defects": c.defect_count,
            "signature": c.signature(), "generation": c.generation,
            "elements": list(set(n.element for n in c.nodes)),
        }


def demo():
    engine = CrystallineLatticeEngine()
    print("=== Crystalline Lattice Engine ===")

    c1 = engine.grow("silicon_cubic", "silicon_seed_42", layers=3, symmetry="cubic")
    c2 = engine.grow("carbon_hex", "carbon_diamond", layers=2, symmetry="hexagonal")
    c3 = engine.grow("germanium_cubic", "silicon_seed_42", layers=3, symmetry="cubic")

    for name in ["silicon_cubic", "carbon_hex", "germanium_cubic"]:
        info = engine.lattice_info(name)
        print(f"\n  {name}:")
        print(f"    Nodes: {info['nodes']}, Volume: {info['volume']}, "
              f"Density: {info['density']}")
        print(f"    Elements: {info['elements']}, Signature: {info['signature']}")

    engine.introduce_defects("silicon_cubic", count=3)
    print(f"\n  Defects in silicon_cubic: {engine.lattice_info('silicon_cubic')['defects']}")

    comparison = engine.compare("silicon_cubic", "germanium_cubic")
    print(f"\n  silicon_cubic vs germanium_cubic:")
    print(f"    Shared elements: {comparison['shared_elements']}")
    print(f"    Same seed -> same signature: "
          f"{comparison['a_signature'] == comparison['b_signature']}")

    return {"crystals": [engine.lattice_info(n) for n in engine.crystals]}


if __name__ == "__main__":
    demo()
