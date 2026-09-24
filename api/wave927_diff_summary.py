"""Wave 927 — Diff Summary.

Produces a compact deterministic summary of a Wave 926 state diff.
"""
from __future__ import annotations
from typing import Any, Dict

def summarize(diff: Dict[str, Any]) -> Dict[str, Any]:
    fields=sorted(str(v) for v in (diff.get("changed_fields") or []))
    return {
        "wave":927,
        "changed":bool(fields),
        "changed_fields":fields,
        "change_count":len(fields),
        "interpretation":"descriptive_diff_summary_only",
    }

def handler(payload: Dict[str, Any]|None=None)->Dict[str, Any]:
    payload=payload or {}; action=payload.get("action","status")
    if action=="summarize": return summarize(payload.get("diff",{}))
    if action=="status": return {"wave":927,"name":"diff_summary","status":"experimental"}
    return {"error":"unknown action","available":["status","summarize"]}

def coherence_vitals()->dict:
    return {"layer":"experimental","status":"active","wave":"927","module":"diff_summary"}

def resonates_with()->list:
    return ["wave926_snapshot_diff","wave925_audit_snapshot"]
