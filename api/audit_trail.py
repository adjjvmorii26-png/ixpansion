"""Wave 136 — Audit Trail.

An append-only, tamper-evident ledger of every civilization action.
Each entry is chained to the previous via a hash, so any alteration
breaks the chain and is immediately detectable — giving full
accountability for the workforce.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class AuditTrail:
    """Append-only, hash-chained accountability ledger."""

    def __init__(self):
        self._entries: List[Dict[str, Any]] = []
        self._tail_hash = hashlib.sha256(b"genesis").hexdigest()

    def append(self, actor: str, action: str, detail: str = "") -> str:
        record = {
            "actor": actor, "action": action, "detail": detail,
            "timestamp": round(time.time(), 4),
            "prev_hash": self._tail_hash,
        }
        payload = f"{actor}:{action}:{detail}:{record['prev_hash']}".encode()
        record["hash"] = hashlib.sha256(payload).hexdigest()
        self._entries.append(record)
        self._tail_hash = record["hash"]
        return record["hash"]

    def verify(self) -> bool:
        """Confirms the chain is intact (tamper-evident)."""
        prev = hashlib.sha256(b"genesis").hexdigest()
        for entry in self._entries:
            if entry["prev_hash"] != prev:
                return False
            payload = f"{entry['actor']}:{entry['action']}:{entry['detail']}:{entry['prev_hash']}".encode()
            if hashlib.sha256(payload).hexdigest() != entry["hash"]:
                return False
            prev = entry["hash"]
        return True

    def entries(self, actor: Optional[str] = None) -> List[Dict[str, Any]]:
        if actor is None:
            return list(self._entries)
        return [e for e in self._entries if e["actor"] == actor]

    def status(self) -> Dict[str, Any]:
        return {"entries": len(self._entries), "intact": self.verify(),
                "tail_hash": self._tail_hash[:12]}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    trail = AuditTrail()
    return {"status": "active", "module": "audit_trail",
            **trail.status()}

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "protocol", "status": "active", "wave": "136", "module": "audit_trail"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
