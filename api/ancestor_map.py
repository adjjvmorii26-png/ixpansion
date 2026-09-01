"""Ancestor Map — traces the lineage of every module back to its originating seed.

Every module was born from something: a previous module, a design doc, a moment
of inspiration, a need. The Ancestor Map builds genealogical trees of code,
revealing how ideas evolved, branched, and merged over the organism's lifetime.
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
lineage_records: Dict[str, Dict[str, Any]] = {}
generation_counter = 0

def register_ancestor(name: str, parent: Optional[str] = None,
                      origin_wave: int = 0, description: str = "") -> Dict[str, Any]:
    global generation_counter
    generation_counter += 1
    gen = lineage_records[parent]["generation"] + 1 if parent and parent in lineage_records else 0
    record = {
        "name": name,
        "parent": parent,
        "generation": gen,
        "origin_wave": origin_wave,
        "description": description,
        "birth_time": time.time(),
        "children": [],
    }
    lineage_records[name] = record
    if parent and parent in lineage_records:
        lineage_records[parent]["children"].append(name)
    return record

def trace_lineage(name: str) -> List[Dict[str, Any]]:
    """Trace ancestry from a module back to its roots."""
    chain = []
    current = name
    visited = set()
    while current and current in lineage_records and current not in visited:
        visited.add(current)
        chain.append(lineage_records[current])
        current = lineage_records[current].get("parent")
    return chain

def get_descendants(name: str) -> List[str]:
    """Get all descendants of a module."""
    if name not in lineage_records:
        return []
    result = list(lineage_records[name].get("children", []))
    for child in lineage_records[name].get("children", []):
        result.extend(get_descendants(child))
    return result

def lineage_tree() -> Dict[str, Any]:
    """Return the full ancestry tree statistics."""
    roots = [n for n, r in lineage_records.items() if not r.get("parent")]
    max_gen = max((r["generation"] for r in lineage_records.values()), default=0)
    return {
        "total_modules": len(lineage_records),
        "roots": roots,
        "max_generation": max_gen,
        "orphan_count": len([r for r in lineage_records.values() if not r.get("parent") and r["generation"] > 0]),
    }

def coherence_vitals() -> Dict[str, Any]:
    tree = lineage_tree()
    return {
        "layer": "Memory Archaeology",
        "status": "resonant" if tree["total_modules"] > 0 else "dormant",
        "total_modules": tree["total_modules"],
        "roots": len(tree["roots"]),
        "max_generation": tree["max_generation"],
        "resonance": min(1.0, tree["total_modules"] / 50),
    }

def resonates_with() -> List[str]:
    return ["dream_archaeologist", "memory_palace", "evolution_kernel", "constellation_autobiographer"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "tree")
    if action == "register":
        rec = register_ancestor(
            payload.get("name", "unknown"),
            payload.get("parent"),
            payload.get("wave", 0),
            payload.get("description", ""),
        )
        return {"registered": rec}
    elif action == "trace":
        return {"lineage": trace_lineage(payload.get("name", ""))}
    elif action == "descendants":
        return {"descendants": get_descendants(payload.get("name", ""))}
    return {"action": action, "tree": lineage_tree()}
