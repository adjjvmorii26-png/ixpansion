"""Runtime IO — best-effort persistence for the serverless frontier.

Vercel function filesystems are read-only except /tmp. Any module that
persists state to .runtime/ must never crash when the write fails — a
living organ that dies on disk pressure is no organ at all.  This helper
mirrors the coherence regulator's pattern: try, and on failure degrade
to in-memory mode instead of raising.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


def load_json(path: Path, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Read a JSON state file, returning a default on any failure."""
    default = {} if default is None else dict(default)
    try:
        if path.exists():
            data = json.loads(path.read_text())
            if isinstance(data, dict):
                return dict(data)
    except (OSError, json.JSONDecodeError):
        pass
    return default


def save_json(path: Path, data: Dict[str, Any]) -> bool:
    """Write JSON state best-effort; returns True if persisted, False if not.

    Falls back silently on read-only filesystems (serverless) so callers
    keep working with in-memory state for the duration of the request.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))
        return True
    except OSError:
        return False


def memory_persist(memory: Dict[str, Any], key: str, timestamp: float) -> None:
    """Keep a tiny ring of in-memory snapshots when disk is unavailable."""
    ring = memory.setdefault("_mem_ring", [])
    ring.insert(0, {"t": timestamp, "snapshot": key})
    memory["_mem_ring"] = ring[:8]

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "data", "status": "active", "wave": "0", "module": "runtime_io"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "runtime_io", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
