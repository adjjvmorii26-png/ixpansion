"""Wave 920 — Memory Replay.

Replays descriptive retrieval steps from an explainable query result.
Replay is a trace artifact, not a new inference engine.
"""
from __future__ import annotations
from typing import Any, Dict, List

def replay(explanation: Dict[str, Any]) -> Dict[str, Any]:
    tokens = sorted(str(v) for v in (explanation.get("tokens") or []))
    matched = sorted(str(v) for v in (explanation.get("matched_memory_ids") or []))
    missing = sorted(str(v) for v in (explanation.get("missing_tokens") or []))
    return {
        "wave": 920,
        "query": explanation.get("query", ""),
        "steps": [
            {"step": "normalize_tokens", "tokens": tokens},
            {"step": "resolve_token_union", "memory_ids": matched},
            {"step": "record_missing_tokens", "tokens": missing},
        ],
        "method": explanation.get("method", "unknown"),
        "replay_only": True,
    }

def handler(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action", "status")
    if action == "replay":
        return replay(payload.get("explanation", {}))
    if action == "status":
        return {"wave": 920, "name": "memory_replay", "status": "experimental"}
    return {"error": "unknown action", "available": ["status", "replay"]}

def coherence_vitals() -> dict:
    return {"layer": "experimental", "status": "active", "wave": "920", "module": "memory_replay"}

def resonates_with() -> list:
    return ["wave919_query_explain", "wave918_memory_query"]
