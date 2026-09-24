"""Wave 919 — Query Explain.

Explains how a descriptive memory query resolved without introducing ranking,
confidence, or truth claims.
"""
from __future__ import annotations
from typing import Any, Dict

def explain(result: Dict[str, Any]) -> Dict[str, Any]:
    tokens = list(result.get("tokens") or [])
    missing = list(result.get("missing_tokens") or [])
    ids = list(result.get("memory_ids") or [])
    return {
        "wave": 919,
        "query": result.get("query", ""),
        "tokens": tokens,
        "matched_memory_ids": sorted(str(v) for v in ids),
        "missing_tokens": sorted(str(v) for v in missing),
        "match_count": len(ids),
        "method": "token_union",
        "interpretation": "descriptive_retrieval_only",
    }

def handler(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    if payload.get("action", "status") == "explain":
        return explain(payload.get("result", {}))
    if payload.get("action", "status") == "status":
        return {"wave": 919, "name": "query_explain", "status": "experimental"}
    return {"error": "unknown action", "available": ["status", "explain"]}

def coherence_vitals() -> dict:
    return {"layer": "experimental", "status": "active", "wave": "919", "module": "query_explain"}

def resonates_with() -> list:
    return ["wave918_memory_query", "wave917_memory_index"]
