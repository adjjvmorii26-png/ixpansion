"""Wave 928 — Diff History.

Maintains an ordered descriptive history of Wave 927 summaries.
"""
from __future__ import annotations
from typing import Any, Dict, List

def append(history: List[Dict[str, Any]]|None, summary: Dict[str, Any])->Dict[str, Any]:
    items=[dict(x) for x in (history or [])]
    item=dict(summary)
    item["sequence"]=len(items)
    items.append(item)
    return {"wave":928,"history":items,"count":len(items),
            "interpretation":"descriptive_history_only"}

def handler(payload: Dict[str, Any]|None=None)->Dict[str, Any]:
    payload=payload or {}; action=payload.get("action","status")
    if action=="append": return append(payload.get("history",[]),payload.get("summary",{}))
    if action=="status": return {"wave":928,"name":"diff_history","status":"experimental"}
    return {"error":"unknown action","available":["status","append"]}

def coherence_vitals()->dict:
    return {"layer":"experimental","status":"active","wave":"928","module":"diff_history"}

def resonates_with()->list:
    return ["wave927_diff_summary","wave926_snapshot_diff"]
