"""Wave 139 — Deployment Log.

Records a durable history of every deployment: version, wave, commit,
and timestamp. Each release appends a log entry, and the platform
can trace which deployment produced the current live surface.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / ".runtime" / "deployments.json"


class DeploymentLog:
    """Appends and reads deployment history."""

    def __init__(self, path: str = ""):
        self.path = Path(path) if path else LOG_PATH
        self._entries: List[Dict[str, Any]] = self._read()

    def _read(self) -> List[Dict[str, Any]]:
        try:
            if self.path.exists():
                return json.loads(self.path.read_text())
        except (OSError, json.JSONDecodeError):
            pass
        return []

    def record(self, version: str, wave: str, commit: str = "") -> Dict[str, Any]:
        entry = {
            "version": version, "wave": wave, "commit": commit,
            "timestamp": round(time.time(), 4),
            "id": hashlib.sha256(f"{version}:{wave}:{time.time()}".encode()).hexdigest()[:10],
        }
        self._entries.append(entry)
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self._entries, indent=2))
        except OSError:
            pass
        return entry

    def latest(self) -> Dict[str, Any]:
        return self._entries[-1] if self._entries else {"version": "unknown"}

    def status(self) -> Dict[str, Any]:
        return {"deployments": len(self._entries), "latest": self.latest()}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    log = DeploymentLog()
    return {"status": "active", "module": "deployment_log",
            **log.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "protocol", "status": "active", "wave": "139", "module": "deployment_log"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
