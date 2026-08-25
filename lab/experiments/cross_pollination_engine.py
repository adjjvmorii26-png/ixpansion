from __future__ import annotations
"""Cross-Pollination Engine — finds hidden connections between subsystems.

Like pollinators that carry pollen between distant flowers, this engine
finds unexpected connections between the constellation, mycelium,
solid-organism, and lab subsystems. It identifies "pollination vectors"
— paths through which ideas can flow between previously unconnected areas.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

@dataclass
class PollinationVector:
    source_system: str
    source_concept: str
    target_system: str
    target_concept: str
    strength: float
    path: List[str]
    novelty: float = 0.0

class CrossPollinationEngine:
    def __init__(self):
        self.subsystems: Dict[str, Dict[str, float]] = {}
        self.vectors: List[PollinationVector] = {}
        self.known_connections: Set[Tuple[str, str, str, str]] = set()

    def register_concept(self, system: str, concept: str, embedding: List[float] = None):
        if system not in self.subsystems:
            self.subsystems[system] = {}
        if embedding is None:
            h = hashlib.md5(f"{system}:{concept}".encode()).digest()
            embedding = [h[i] / 255.0 for i in range(min(8, len(h)))]
        self.subsystems[system][concept] = embedding

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        n = min(len(a), len(b))
        if n == 0:
            return 0.0
        dot = sum(a[i] * b[i] for i in range(n))
        mag_a = math.sqrt(sum(x * x for x in a[:n]))
        mag_b = math.sqrt(sum(x * x for x in b[:n]))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    def discover_vectors(self, threshold: float = 0.3) -> List[PollinationVector]:
        self.vectors = []
        systems = list(self.subsystems.keys())
        for i, sys_a in enumerate(systems):
            for sys_b in systems[i + 1:]:
                for concept_a, embed_a in self.subsystems[sys_a].items():
                    for concept_b, embed_b in self.subsystems[sys_b].items():
                        sim = self._cosine_similarity(embed_a, embed_b)
                        if sim > threshold:
                            key = (sys_a, concept_a, sys_b, concept_b)
                            novelty = 1.0 if key not in self.known_connections else 0.5
                            vector = PollinationVector(
                                source_system=sys_a, source_concept=concept_a,
                                target_system=sys_b, target_concept=concept_b,
                                strength=round(sim, 4),
                                path=[sys_a, concept_a, concept_b, sys_b],
                                novelty=novelty,
                            )
                            self.vectors.append(vector)
                            self.known_connections.add(key)
        self.vectors.sort(key=lambda v: v.strength, reverse=True)
        return self.vectors

    def pollination_map(self) -> Dict:
        system_pairs = {}
        for v in self.vectors:
            pair = f"{v.source_system}→{v.target_system}"
            system_pairs[pair] = system_pairs.get(pair, 0) + 1
        return {
            "total_vectors": len(self.vectors),
            "system_pairs": system_pairs,
            "novel_vectors": sum(1 for v in self.vectors if v.novelty > 0.7),
            "top_vectors": [
                {"from": f"{v.source_system}.{v.source_concept}",
                 "to": f"{v.target_system}.{v.target_concept}",
                 "strength": v.strength, "novel": v.novelty > 0.7}
                for v in self.vectors[:10]
            ],
        }


def demo():
    engine = CrossPollinationEngine()
    print("=== Cross-Pollination Engine ===")
    engine.register_concept("constellation", "treaty_negotiation")
    engine.register_concept("constellation", "atlas_compilation")
    engine.register_concept("mycelium", "dream_compilation")
    engine.register_concept("mycelium", "hyphal_growth")
    engine.register_concept("solid-organism", "kintsugi_repair")
    engine.register_concept("solid-organism", "cordyceps_spread")
    engine.register_concept("lab", "photon_memory")
    engine.register_concept("lab", "coral_growth")
    vectors = engine.discover_vectors(threshold=0.1)
    print(f"  Vectors discovered: {len(vectors)}")
    pmap = engine.pollination_map()
    print(f"  System pairs: {pmap['system_pairs']}")
    print(f"  Novel vectors: {pmap['novel_vectors']}")
    print("  Top vectors:")
    for v in pmap["top_vectors"][:5]:
        print(f"    {v['from']} → {v['to']}: {v['strength']} "
              f"{'[NOVEL]' if v['novel'] else ''}")
    return pmap


if __name__ == "__main__":
    demo()
