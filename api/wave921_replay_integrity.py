"""Wave 921 — Replay Integrity.

Creates a deterministic digest for replay traces so downstream tooling can
detect accidental mutation without interpreting the trace as truth.
"""
from __future__ import annotations
import hashlib, json
from typing import Any, Dict

def fingerprint(replay_trace: Dict[str, Any]) -> str:
    canonical = json.dumps(replay_trace, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]

def attest(replay_trace: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "wave": 921,
        "fingerprint": fingerprint(replay_trace),
        "integrity_only": True,
        "interpretation": "mutation_detection_only",
    }

def handler(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action", "status")
    if action == "fingerprint":
        return {"fingerprint": fingerprint(payload.get("replay", {}))}
    if action == "attest":
        return attest(payload.get("replay", {}))
    if action == "status":
        return {"wave": 921, "name": "replay_integrity", "status": "experimental"}
    return {"error": "unknown action", "available": ["status", "fingerprint", "attest"]}

def coherence_vitals() -> dict:
    return {"layer": "experimental", "status": "active", "wave": "921", "module": "replay_integrity"}

def resonates_with() -> list:
    return ["wave920_memory_replay", "wave919_query_explain"]
