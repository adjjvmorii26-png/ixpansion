"""
module_genealogy — Tracks the ancestry, lineage, and evolutionary history of modules.
Every module has parents, traits inherited, and mutations that distinguish it.
"""
import json
import time
import hashlib
from typing import Dict, List, Optional
from pathlib import Path

SYSTEM_ROOT = Path("/root/Documents/Codex/2026-08-22/chmod-x-nexus-observatory-nexus-boot")

_skill_active = False
_lineage_graph = {}
_birth_registry = []
_trait_pool = [
    "resonance_sensitivity", "entropy_absorption", "fractal_recursion",
    "paradox_tolerance", "coherence_amplification", "memory_depth",
    "dream_permeability", "temporal_fluidity", "spatial_expansion",
    "signal_clarity", "noise_resilience", "harmonic_generation",
    "mutation_resistance", "adaptation_speed", "cross_module_empathy"
]

def activate_skill(params=None):
    global _skill_active
    _skill_active = True
    return {"status": "activated", "skill": "module_genealogy", "activated_at": time.time()}

def register_birth(module_name: str, parent_modules: List[str] = None, 
                   generation: int = 0, traits: List[str] = None) -> Dict:
    import random
    
    if not traits:
        traits = random.sample(_trait_pool, min(3, len(_trait_pool)))
    
    birth_record = {
        "name": module_name,
        "birth_id": hashlib.sha256(f"{module_name}{time.time()}".encode()).hexdigest()[:10],
        "parents": parent_modules or [],
        "generation": generation,
        "inherited_traits": traits,
        "mutations": [],
        "birth_time": time.time(),
        "children": []
    }
    
    _lineage_graph[module_name] = birth_record
    
    # Register as child of parents
    for parent in (parent_modules or []):
        if parent in _lineage_graph:
            _lineage_graph[parent]["children"].append(module_name)
    
    _birth_registry.append(birth_record)
    return birth_record

def trace_lineage(module_name: str) -> Dict:
    if module_name not in _lineage_graph:
        return {"error": f"Module '{module_name}' not found in lineage graph"}
    
    record = _lineage_graph[module_name]
    
    # Walk up to root
    ancestors = []
    current = module_name
    visited = set()
    while current in _lineage_graph and current not in visited:
        visited.add(current)
        ancestors.append(current)
        parents = _lineage_graph[current]["parents"]
        current = parents[0] if parents else None
    
    # Walk down to leaves
    descendants = []
    queue = [module_name]
    visited_d = set()
    while queue:
        node = queue.pop(0)
        if node not in visited_d and node in _lineage_graph:
            visited_d.add(node)
            if node != module_name:
                descendants.append(node)
            queue.extend(_lineage_graph[node]["children"])
    
    return {
        "module": module_name,
        "generation": record["generation"],
        "parents": record["parents"],
        "inherited_traits": record["inherited_traits"],
        "mutations": record["mutations"],
        "ancestors": list(reversed(ancestors)),
        "descendants": descendants,
        "lineage_depth": len(ancestors),
        "branch_count": len(descendants)
    }

def get_all_lineages() -> Dict:
    return {
        "total_modules": len(_lineage_graph),
        "total_births": len(_birth_registry),
        "generations": max((r["generation"] for r in _lineage_graph.values()), default=0) + 1,
        "trait_pool_size": len(_trait_pool),
        "modules": list(_lineage_graph.keys())
    }

def get_skill_state():
    return {
        "name": "module_genealogy",
        "active": _skill_active,
        "capabilities": ["register_birth", "trace_lineage", "get_all_lineages"],
        "total_modules_in_graph": len(_lineage_graph),
        "total_births": len(_birth_registry)
    }
