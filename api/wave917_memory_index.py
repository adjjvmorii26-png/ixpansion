"""Wave 917 — Memory Index.

Builds a deterministic descriptive index over Wave 916 memories.
It exposes exact token matches and provenance context without ranking memories
or converting matches into truth claims.
"""
from __future__ import annotations
from typing import Any, Dict, List

def _tokens(value: Any) -> List[str]:
    return sorted(set(str(value or "").lower().split()))

def build_index(memories: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    items = memories or []
    index: Dict[str, List[str]] = {}
    for memory in items:
        memory_id = str(memory.get("id", ""))
        for token in _tokens(memory.get("content")):
            index.setdefault(token, []).append(memory_id)
    for token in index:
        index[token] = sorted(set(index[token]))
    return {
        "wave": 917,
        "name": "memory_index",
        "tokens": {k: index[k] for k in sorted(index)},
        "policy": {
            "descriptive_only": True,
            "no_ranking": True,
            "no_truth_inference": True,
        },
    }

def lookup(index: Dict[str, Any], query: str) -> Dict[str, Any]:
    token = str(query or "").lower().strip()
    ids = list((index.get("tokens") or {}).get(token, []))
    return {"query": query, "memory_ids": ids, "match_count": len(ids)}

def handler(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action", "status")
    if action == "build":
        return build_index(payload.get("memories", []))
    if action == "lookup":
        return lookup(payload.get("index", {}), str(payload.get("query", "")))
    if action == "status":
        return {"wave": 917, "name": "memory_index", "status": "experimental"}
    return {"error": "unknown action", "available": ["status", "build", "lookup"]}

def coherence_vitals() -> dict:
    return {"layer": "experimental", "status": "active", "wave": "917", "module": "memory_index"}

def resonates_with() -> list:
    return ["wave916_evolution_memory", "wave915_invariant_genealogy"]
