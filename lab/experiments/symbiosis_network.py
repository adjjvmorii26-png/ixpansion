"""
symbiosis_network — Models cooperative relationships between organism modules.
Modules form symbiotic bonds: mutualism, commensalism, or parasitism.
The network evolves as bonds strengthen, weaken, or transform.
"""
import json
import time
import hashlib
import random
import math
from typing import Dict, List, Tuple

BOND_TYPES = {
    "mutualism": {"desc": "Both modules benefit", "strength_delta": 0.05, "glyph": "⊕"},
    "commensalism": {"desc": "One benefits, other unaffected", "strength_delta": 0.02, "glyph": "⊗"},
    "parasitism": {"desc": "One benefits at other's expense", "strength_delta": -0.03, "glyph": "⊘"},
    "neutralism": {"desc": "Neither affected", "strength_delta": 0, "glyph": "⊙"},
    "competition": {"desc": "Both harmed by rivalry", "strength_delta": -0.05, "glyph": "⊖"}
}

class SymbiosisNetwork:
    def __init__(self):
        self.bonds = []
        self.history = []
    
    def form_bond(self, module_a: str, module_b: str, bond_type: str = None) -> Dict:
        if not bond_type:
            bond_type = random.choices(
                list(BOND_TYPES.keys()),
                weights=[40, 25, 10, 15, 10]
            )[0]
        
        bond = {
            "id": hashlib.sha256(f"{module_a}{module_b}{time.time()}".encode()).hexdigest()[:8],
            "module_a": module_a,
            "module_b": module_b,
            "type": bond_type,
            "strength": random.uniform(0.3, 0.8),
            "formed_at": time.time(),
            "interactions": 0,
            "description": BOND_TYPES[bond_type]["desc"],
            "glyph": BOND_TYPES[bond_type]["glyph"]
        }
        
        self.bonds.append(bond)
        return bond
    
    def interact(self, bond_id: str) -> Dict:
        bond = next((b for b in self.bonds if b["id"] == bond_id), None)
        if not bond:
            return {"error": "bond not found"}
        
        bond["interactions"] += 1
        delta = BOND_TYPES[bond["type"]]["strength_delta"]
        bond["strength"] = max(0, min(1, bond["strength"] + delta + random.uniform(-0.02, 0.02)))
        
        # Random type mutation
        if random.random() < 0.05:
            old_type = bond["type"]
            bond["type"] = random.choice(list(BOND_TYPES.keys()))
            bond["description"] = BOND_TYPES[bond["type"]]["desc"]
            bond["glyph"] = BOND_TYPES[bond["type"]]["glyph"]
        
        return {
            "bond_id": bond["id"],
            "strength": round(bond["strength"], 4),
            "interactions": bond["interactions"],
            "type": bond["type"]
        }
    
    def get_network_state(self) -> Dict:
        if not self.bonds:
            return {"bonds": 0, "modules": 0}
        
        type_counts = {}
        total_strength = 0
        modules = set()
        
        for b in self.bonds:
            type_counts[b["type"]] = type_counts.get(b["type"], 0) + 1
            total_strength += b["strength"]
            modules.add(b["module_a"])
            modules.add(b["module_b"])
        
        avg_strength = total_strength / len(self.bonds)
        
        return {
            "total_bonds": len(self.bonds),
            "unique_modules": len(modules),
            "type_distribution": type_counts,
            "average_strength": round(avg_strength, 4),
            "strongest_bond": max(self.bonds, key=lambda b: b["strength"])["id"] if self.bonds else None,
            "weakest_bond": min(self.bonds, key=lambda b: b["strength"])["id"] if self.bonds else None,
            "health": "thriving" if avg_strength > 0.6 else "stable" if avg_strength > 0.4 else "stressed"
        }
    
    def find_clusters(self) -> List[List[str]]:
        """Find connected components (symbiotic clusters)."""
        adj = {}
        for b in self.bonds:
            adj.setdefault(b["module_a"], set()).add(b["module_b"])
            adj.setdefault(b["module_b"], set()).add(b["module_a"])
        
        visited = set()
        clusters = []
        
        for node in adj:
            if node not in visited:
                cluster = []
                stack = [node]
                while stack:
                    n = stack.pop()
                    if n not in visited:
                        visited.add(n)
                        cluster.append(n)
                        stack.extend(adj.get(n, set()) - visited)
                clusters.append(cluster)
        
        return clusters


if __name__ == "__main__":
    net = SymbiosisNetwork()
    
    modules = ["coherence_core", "entropy_field", "resonance_nexus", 
               "dream_weaver", "paradox_engine", "fractal_spine",
               "wave_orchestrator", "memory_archivist"]
    
    print("═══════════════════════════════════════")
    print("   SYMBIOSIS NETWORK — Cooperative Bonds")
    print("═══════════════════════════════════════")
    
    # Form bonds
    for i in range(len(modules)):
        for j in range(i+1, min(i+3, len(modules))):
            bond = net.form_bond(modules[i], modules[j])
            print(f"  {bond['glyph']} {bond['module_a']} ↔ {bond['module_b']} [{bond['type']}] strength={bond['strength']:.2f}")
    
    print()
    
    # Interact
    for bond in net.bonds[:5]:
        result = net.interact(bond["id"])
        print(f"  Interaction: {result['bond_id']} → strength={result['strength']}, interactions={result['interactions']}")
    
    # State
    state = net.get_network_state()
    print(f"\nNetwork: {state['total_bonds']} bonds, {state['unique_modules']} modules")
    print(f"Health: {state['health']}")
    print(f"Type distribution: {state['type_distribution']}")
    
    # Clusters
    clusters = net.find_clusters()
    print(f"\nSymbiotic clusters: {len(clusters)}")
    for i, c in enumerate(clusters):
        print(f"  Cluster {i+1}: {', '.join(c)}")
