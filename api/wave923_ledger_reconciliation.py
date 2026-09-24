"""Wave 923 — Ledger Reconciliation.

Compares two integrity-ledger snapshots structurally. Reconciliation reports
added, removed, and changed sequence entries without declaring either snapshot
correct.
"""
from __future__ import annotations
import json
from typing import Any, Dict

def _canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), default=str)

def reconcile(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    left = {str(x.get("sequence")): x for x in (before.get("entries") or [])}
    right = {str(x.get("sequence")): x for x in (after.get("entries") or [])}
    added = sorted(set(right) - set(left), key=lambda x: int(x) if x.isdigit() else x)
    removed = sorted(set(left) - set(right), key=lambda x: int(x) if x.isdigit() else x)
    changed = sorted(k for k in set(left) & set(right) if _canonical(left[k]) != _canonical(right[k]))
    return {
        "wave": 923,
        "added_sequences": added,
        "removed_sequences": removed,
        "changed_sequences": changed,
        "counts": {"added": len(added), "removed": len(removed), "changed": len(changed)},
        "interpretation": "structural_reconciliation_only",
    }

def handler(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action", "status")
    if action == "reconcile":
        return reconcile(payload.get("before", {}), payload.get("after", {}))
    if action == "status":
        return {"wave": 923, "name": "ledger_reconciliation", "status": "experimental"}
    return {"error": "unknown action", "available": ["status", "reconcile"]}

def coherence_vitals() -> dict:
    return {"layer": "experimental", "status": "active", "wave": "923", "module": "ledger_reconciliation"}

def resonates_with() -> list:
    return ["wave922_integrity_ledger", "wave921_replay_integrity"]
