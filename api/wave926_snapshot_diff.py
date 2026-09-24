"""Wave 926 — Snapshot Diff.

Compares two Wave 925 audit snapshots as normalized state. The result reports
structural field changes without judging which snapshot is correct.
"""
from __future__ import annotations
from typing import Any, Dict

_FIELDS=("status","counts","sequences")

def diff(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    left=before.get("snapshot") or {}
    right=after.get("snapshot") or {}
    changes={}
    for field in _FIELDS:
        if left.get(field) != right.get(field):
            changes[field]={"before":left.get(field),"after":right.get(field)}
    return {
        "wave":926,
        "changed_fields":sorted(changes),
        "changes":{k:changes[k] for k in sorted(changes)},
        "change_count":len(changes),
        "interpretation":"state_diff_only",
    }

def handler(payload: Dict[str, Any]|None=None)->Dict[str, Any]:
    payload=payload or {}; action=payload.get("action","status")
    if action=="diff": return diff(payload.get("before",{}),payload.get("after",{}))
    if action=="status": return {"wave":926,"name":"snapshot_diff","status":"experimental"}
    return {"error":"unknown action","available":["status","diff"]}

def coherence_vitals()->dict:
    return {"layer":"experimental","status":"active","wave":"926","module":"snapshot_diff"}

def resonates_with()->list:
    return ["wave925_audit_snapshot","wave924_reconciliation_audit"]
