"""Wave 931 — Window Integrity.

Adds a deterministic fingerprint to a selected history window.
"""
from __future__ import annotations
import hashlib, json
from typing import Any, Dict, List

def attest(window: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "start": window.get("start"),
        "limit": window.get("limit"),
        "sequences": list(window.get("sequences") or []),
        "history": list(window.get("history") or []),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return {
        "wave": 931,
        "fingerprint": hashlib.sha256(raw.encode()).hexdigest()[:16],
        "count": len(payload["history"]),
        "interpretation": "window_integrity_only",
    }

def handler(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action", "status")
    if action == "attest":
        return attest(payload.get("window", {}))
    if action == "status":
        return {"wave": 931, "name": "window_integrity", "status": "experimental"}
    return {"error": "unknown action", "available": ["status", "attest"]}

def coherence_vitals() -> dict:
    return {"layer": "experimental", "status": "active", "wave": "931", "module": "window_integrity"}

def resonates_with() -> list:
    return ["wave930_history_window", "wave921_replay_integrity"]
