"""Wave 924 — Reconciliation Audit.

Summarizes structural reconciliation findings with deterministic counts.
This is an audit artifact, not a correctness judgment.
"""
from __future__ import annotations
from typing import Any, Dict

def audit(reconciliation: Dict[str, Any]) -> Dict[str, Any]:
    counts = dict(reconciliation.get("counts") or {})
    added = int(counts.get("added", 0))
    removed = int(counts.get("removed", 0))
    changed = int(counts.get("changed", 0))
    return {
        "wave": 924,
        "status": "delta_present" if (added + removed + changed) else "no_delta",
        "counts": {"added": added, "removed": removed, "changed": changed},
        "total_differences": added + removed + changed,
        "sequences": {
            "added": sorted(str(v) for v in (reconciliation.get("added_sequences") or [])),
            "removed": sorted(str(v) for v in (reconciliation.get("removed_sequences") or [])),
            "changed": sorted(str(v) for v in (reconciliation.get("changed_sequences") or [])),
        },
        "interpretation": "structural_audit_only",
    }

def handler(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action", "status")
    if action == "audit":
        return audit(payload.get("reconciliation", {}))
    if action == "status":
        return {"wave": 924, "name": "reconciliation_audit", "status": "experimental"}
    return {"error": "unknown action", "available": ["status", "audit"]}

def coherence_vitals() -> dict:
    return {"layer": "experimental", "status": "active", "wave": "924", "module": "reconciliation_audit"}

def resonates_with() -> list:
    return ["wave923_ledger_reconciliation", "wave922_integrity_ledger"]
