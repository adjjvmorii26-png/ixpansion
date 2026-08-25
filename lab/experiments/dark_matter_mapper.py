from __future__ import annotations
"""Dark Matter Mapper — maps unseen connections between modules.

Like cosmic dark matter that's detected only by its gravitational effects,
this system detects implicit dependencies between modules through shared
state access, config coupling, timing correlations, and naming resonance.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

@dataclass
class ModuleSignature:
    name: str
    file_hash: str = ""
    imports: Set[str] = field(default_factory=set)
    exports: Set[str] = field(default_factory=set)
    config_keys: Set[str] = field(default_factory=set)
    naming_patterns: List[str] = field(default_factory=list)
    entropy: float = 0.0

    def __post_init__(self):
        if not self.file_hash:
            raw = f"{self.name}:{sorted(self.imports)}:{sorted(self.exports)}"
            self.file_hash = hashlib.md5(raw.encode()).hexdigest()[:12]


@dataclass
class DarkConnection:
    module_a: str
    module_b: str
    strength: float
    connection_type: str
    evidence: List[str] = field(default_factory=list)


class DarkMatterMapper:
    def __init__(self):
        self.modules: Dict[str, ModuleSignature] = {}
        self.connections: List[DarkConnection] = []
        self.gravitational_field: Dict[str, float] = {}

    def register_module(self, name: str, imports: List[str] = None,
                        exports: List[str] = None, config_keys: List[str] = None,
                        source_code: str = "") -> ModuleSignature:
        sig = ModuleSignature(
            name=name,
            imports=set(imports or []),
            exports=set(exports or []),
            config_keys=set(config_keys or []),
        )
        if source_code:
            sig.entropy = self._shannon_entropy(source_code)
            sig.naming_patterns = self._extract_naming_patterns(source_code)
        self.modules[name] = sig
        self.gravitational_field[name] = 0.0
        return sig

    def _shannon_entropy(self, text: str) -> float:
        if not text:
            return 0.0
        freq = {}
        for c in text:
            freq[c] = freq.get(c, 0) + 1
        length = len(text)
        return -sum(
            (count / length) * math.log2(count / length)
            for count in freq.values() if count > 0
        )

    def _extract_naming_patterns(self, code: str) -> List[str]:
        import re
        words = re.findall(r'[a-z_]+', code)
        patterns = []
        for w in words:
            if len(w) > 4:
                patterns.append(w[-4:])
        return list(set(patterns))[:20]

    def _explicit引力(self, a: ModuleSignature, b: ModuleSignature) -> float:
        shared_imports = a.imports & b.imports
        shared_configs = a.config_keys & b.config_keys
        shared_naming = set(a.naming_patterns) & set(b.naming_patterns)
        score = (len(shared_imports) * 0.3 +
                 len(shared_configs) * 0.2 +
                 len(shared_naming) * 0.1)
        return min(score, 1.0)

    def _temporal_correlation(self, a: ModuleSignature, b: ModuleSignature) -> float:
        entropy_diff = abs(a.entropy - b.entropy)
        max_entropy = 8.0
        return max(0, 1.0 - entropy_diff / max_entropy)

    def _naming_resonance(self, a: ModuleSignature, b: ModuleSignature) -> float:
        hash_a = int(a.file_hash, 16)
        hash_b = int(b.file_hash, 16)
        xor = hash_a ^ hash_b
        hamming = bin(xor).count("1")
        return max(0, 1.0 - hamming / 64.0)

    def scan(self) -> List[DarkConnection]:
        self.connections.clear()
        names = list(self.modules.keys())
        for i, na in enumerate(names):
            for nb in names[i + 1:]:
                a, b = self.modules[na], self.modules[nb]
                explicit = self._explicit引力(a, b)
                temporal = self._temporal_correlation(a, b)
                naming = self._naming_resonance(a, b)
                total = explicit * 0.4 + temporal * 0.3 + naming * 0.3

                evidence = []
                if explicit > 0.1:
                    shared = a.imports & b.imports
                    if shared:
                        evidence.append(f"shared imports: {shared}")
                    shared_cfg = a.config_keys & b.config_keys
                    if shared_cfg:
                        evidence.append(f"shared config: {shared_cfg}")
                if temporal > 0.8:
                    evidence.append(f"entropy similarity: {temporal:.3f}")
                if naming > 0.5:
                    evidence.append(f"naming resonance: {naming:.3f}")

                if total > 0.05:
                    ctype = "explicit" if explicit > 0.3 else (
                        "temporal" if temporal > 0.5 else "naming"
                    )
                    self.connections.append(DarkConnection(
                        module_a=na, module_b=nb,
                        strength=total, connection_type=ctype,
                        evidence=evidence
                    ))

        self.connections.sort(key=lambda c: c.strength, reverse=True)
        for c in self.connections:
            self.gravitational_field[c.module_a] += c.strength
            self.gravitational_field[c.module_b] += c.strength

        return self.connections

    def dark_mass(self, module_name: str) -> float:
        return self.gravitational_field.get(module_name, 0.0)

    def cluster(self, threshold: float = 0.2) -> List[List[str]]:
        adj: Dict[str, Set[str]] = {n: set() for n in self.modules}
        for c in self.connections:
            if c.strength >= threshold:
                adj[c.module_a].add(c.module_b)
                adj[c.module_b].add(c.module_a)
        visited = set()
        clusters = []
        for node in adj:
            if node in visited:
                continue
            cluster = []
            stack = [node]
            while stack:
                n = stack.pop()
                if n in visited:
                    continue
                visited.add(n)
                cluster.append(n)
                stack.extend(adj[n] - visited)
            if cluster:
                clusters.append(sorted(cluster))
        return sorted(clusters, key=len, reverse=True)

    def summary(self) -> dict:
        return {
            "modules": len(self.modules),
            "dark_connections": len(self.connections),
            "strongest": [
                {"a": c.module_a, "b": c.module_b,
                 "strength": round(c.strength, 4)}
                for c in self.connections[:5]
            ],
            "clusters": self.cluster(),
            "gravitational_field": {
                k: round(v, 4) for k, v in sorted(
                    self.gravitational_field.items(),
                    key=lambda x: x[1], reverse=True
                )[:10]
            },
        }


def demo():
    mapper = DarkMatterMapper()
    modules_data = [
        ("photon_memory", ["hashlib", "cmath"], ["store", "read"], ["wavelength"]),
        ("dark_matter_mapper", ["math", "json"], ["scan", "cluster"], []),
        ("tardigrade_survival", ["time", "random"], ["stress_test"], ["timeout"]),
        ("coral_reef", ["random"], ["grow", "compete"], ["nutrient_pool"]),
        ("neutron_star_core", ["math"], ["compress", "decompress"], ["density"]),
        ("thermal_dynamics", ["math"], ["heat_flow"], ["conductivity"]),
        ("silicon_lifeform", ["random", "math"], ["evolve"], ["genome"]),
        ("gravitational_well", ["math"], ["attract", "repel"], ["mass"]),
        ("crystalline_lattice", ["math"], ["grow_crystal"], ["symmetry"]),
        ("neutrino_detector", ["random"], ["detect", "filter"], ["sensitivity"]),
    ]
    for name, imports, exports, configs in modules_data:
        source = " ".join(imports + exports + configs) * 10
        mapper.register_module(name, imports, exports, configs, source)

    connections = mapper.scan()
    print("=== Dark Matter Mapper ===")
    print(f"Modules: {len(mapper.modules)}")
    print(f"Dark connections found: {len(connections)}")
    for c in connections[:10]:
        print(f"  {c.module_a} <-> {c.module_b}: "
              f"strength={c.strength:.4f} type={c.connection_type}")
        for e in c.evidence:
            print(f"    evidence: {e}")

    summary = mapper.summary()
    print(f"\nClusters: {summary['clusters']}")
    print(f"\nGravitational field (top 5):")
    for name, mass in list(summary['gravitational_field'].items())[:5]:
        print(f"  {name}: dark_mass={mass:.4f}")

    return summary


if __name__ == "__main__":
    demo()
