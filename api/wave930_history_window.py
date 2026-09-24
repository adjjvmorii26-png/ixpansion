"""Wave 930 — History Window.

Selects a deterministic contiguous sequence window from descriptive history.
"""
from __future__ import annotations
from typing import Any, Dict, List

def window(history: List[Dict[str, Any]]|None=None, start: int=0, limit: int|None=None)->Dict[str, Any]:
    items=sorted(list(history or []), key=lambda x: (x.get("sequence", 0)))
    start=max(0,int(start))
    selected=items[start:] if limit is None else items[start:start+max(0,int(limit))]
    return {
        "wave":930,
        "start":start,
        "limit":limit,
        "count":len(selected),
        "sequences":[x.get("sequence") for x in selected],
        "history":selected,
        "interpretation":"descriptive_window_only",
    }

def handler(payload: Dict[str, Any]|None=None)->Dict[str, Any]:
    payload=payload or {}; action=payload.get("action","status")
    if action=="window":
        return window(payload.get("history",[]),payload.get("start",0),payload.get("limit"))
    if action=="status":
        return {"wave":930,"name":"history_window","status":"experimental"}
    return {"error":"unknown action","available":["status","window"]}

def coherence_vitals()->dict:
    return {"layer":"experimental","status":"active","wave":"930","module":"history_window"}

def resonates_with()->list:
    return ["wave929_history_query","wave928_diff_history"]
