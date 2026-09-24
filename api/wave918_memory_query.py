"""Wave 918 — Memory Query.

Provides deterministic multi-token lookup over the Wave 917 index.
Results are sets of matching memory IDs with no ranking or confidence.
"""
from __future__ import annotations
from typing import Any, Dict, List

def query(index: Dict[str, Any], text: str) -> Dict[str, Any]:
    tokens = sorted(set(str(text or "").lower().split()))
    table = index.get("tokens") or {}
    matches: set[str] = set()
    missing: List[str] = []
    for token in tokens:
        ids = table.get(token)
        if ids is None:
            missing.append(token)
        else:
            matches.update(str(v) for v in ids)
    return {
        "query": text,
        "tokens": tokens,
        "memory_ids": sorted(matches),
        "missing_tokens": missing,
        "match_count": len(matches),
    }

def handler(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action", "status")
    if action == "query":
        return query(payload.get("index", {}), str(payload.get("query", "")))
    if action == "status":
        return {"wave": 918, "name": "memory_query", "status": "experimental"}
    return {"error": "unknown action", "available": ["status", "query"]}

def coherence_vitals() -> dict:
    return {"layer": "experimental", "status": "active", "wave": "918", "module": "memory_query"}

def resonates_with() -> list:
    return ["wave917_memory_index", "wave916_evolution_memory"]
