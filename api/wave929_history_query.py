"""Wave 929 — History Query.

Provides deterministic filtering over descriptive diff history.
"""
from __future__ import annotations
from typing import Any, Dict, List

def query(history: List[Dict[str, Any]]|None=None, changed: bool|None=None)->Dict[str, Any]:
    items=list(history or [])
    if changed is not None:
        items=[x for x in items if bool(x.get("changed")) is changed]
    return {"wave":929,"count":len(items),"sequences":[x.get("sequence") for x in items],
            "history":items,"interpretation":"descriptive_filter_only"}

def handler(payload: Dict[str, Any]|None=None)->Dict[str, Any]:
    payload=payload or {}; action=payload.get("action","status")
    if action=="query": return query(payload.get("history",[]),payload.get("changed"))
    if action=="status": return {"wave":929,"name":"history_query","status":"experimental"}
    return {"error":"unknown action","available":["status","query"]}

def coherence_vitals()->dict:
    return {"layer":"experimental","status":"active","wave":"929","module":"history_query"}

def resonates_with()->list:
    return ["wave928_diff_history","wave927_diff_summary"]
