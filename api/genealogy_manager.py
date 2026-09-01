"""Genealogy Manager — tracks parent-child lineage of module mutations.

Every mutation creates a new version of a module. The Genealogy Manager
tracks these family trees: which mutations descended from which, which
lines thrived and which died out. This is the organism's evolutionary
history, complete with branches and extinctions.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

_family_tree: Dict[str, Dict[str, Any]] = {}
_generation = 0

def birth(name: str, parent: Optional[str] = None, source_mutation: str = "") -> Dict[str, Any]:
    """Register the birth of a new module version."""
    global _generation
    _generation += 1
    gen = _family_tree[parent]["generation"] + 1 if parent and parent in _family_tree else 0
    record = {
        "name": name,
        "parent": parent,
        "generation": gen,
        "source_mutation": source_mutation,
        "born": time.time(),
        "children": [],
        "status": "alive",
    }
    _family_tree[name] = record
    if parent and parent in _family_tree:
        _family_tree[parent]["children"].append(name)
    return record

def extinct(name: str, cause: str = "selection_pressure") -> Dict[str, Any]:
    """Mark a lineage branch as extinct."""
    if name in _family_tree:
        _family_tree[name]["status"] = "extinct"
        _family_tree[name]["extinction_cause"] = cause
        _family_tree[name]["extinct_at"] = time.time()
        return _family_tree[name]
    return {"error": "lineage not found"}

def trace(name: str) -> List[Dict[str, Any]]:
    """Trace a lineage back to its roots."""
    chain = []
    current = name
    visited = set()
    while current and current in _family_tree and current not in visited:
        visited.add(current)
        chain.append(_family_tree[current])
        current = _family_tree[current].get("parent")
    return chain

def genealogy_report() -> Dict[str, Any]:
    """Full genealogy statistics."""
    alive = sum(1 for r in _family_tree.values() if r["status"] == "alive")
    ext = sum(1 for r in _family_tree.values() if r["status"] == "extinct")
    roots = [n for n, r in _family_tree.items() if not r.get("parent")]
    max_gen = max((r["generation"] for r in _family_tree.values()), default=0)
    return {
        "total_births": len(_family_tree),
        "alive": alive,
        "extinct": ext,
        "roots": roots,
        "generations": max_gen,
        "extinction_rate": round(ext / max(len(_family_tree), 1), 3),
    }

def coherence_vitals() -> Dict[str, Any]:
    report = genealogy_report()
    return {"layer": "Self-Evolution", "status": "resonant", "births": report["total_births"],
            "generations": report["generations"], "resonance": min(1.0, report["total_births"] / 15)}

def resonates_with() -> List[str]:
    return ["mutation_engine", "ancestor_map", "evolution_kernel"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "report")
    if action == "birth":
        return birth(payload.get("name", ""), payload.get("parent"), payload.get("mutation", ""))
    elif action == "extinct":
        return extinct(payload.get("name", ""), payload.get("cause", "selection_pressure"))
    elif action == "trace":
        return {"lineage": trace(payload.get("name", ""))}
    elif action == "report":
        return {"report": genealogy_report()}
    return {"action": action, "status": "genealogical"}
