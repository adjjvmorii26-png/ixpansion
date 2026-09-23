"""Wave 903 — Experiment Chamber.

A sandbox for executing only declarative, deterministic experiment recipes.
No imports, subprocesses, network calls, filesystem writes, or arbitrary code
execution are permitted. The chamber compares a baseline with a small mutation
and records an auditable result.
"""
from __future__ import annotations
import hashlib
from typing import Any, Dict, List

ALLOWED_OPS={"add","remove","replace","duplicate"}

def _digest(value:Any)->str:
    return hashlib.sha256(repr(value).encode()).hexdigest()[:16]

def _apply(events:List[Dict[str,Any]], recipe:Dict[str,Any])->List[Dict[str,Any]]:
    out=[dict(x) for x in events]
    op=recipe.get("op")
    if op not in ALLOWED_OPS: raise ValueError("unsupported experiment operation")
    if op=="add": out.append(dict(recipe.get("event",{})))
    elif op=="duplicate" and out: out.append(dict(out[int(recipe.get("index",0))%len(out)]))
    elif op=="remove" and out: out.pop(int(recipe.get("index",0))%len(out))
    elif op=="replace" and out:
        i=int(recipe.get("index",0))%len(out); out[i]=dict(recipe.get("event",{}))
    return out

def chamber(events:List[Dict[str,Any]], recipes:List[Dict[str,Any]]|None=None)->Dict[str,Any]:
    baseline=[dict(x) for x in events or []]
    results=[]
    for recipe in (recipes or [])[:8]:
        before=_digest(baseline)
        try:
            mutated=_apply(baseline,recipe)
            results.append({"recipe":dict(recipe),"baseline":before,
                            "mutated":_digest(mutated),"changed":mutated!=baseline,
                            "status":"simulated"})
        except (TypeError,ValueError,KeyError) as exc:
            results.append({"recipe":dict(recipe),"baseline":before,
                            "status":"rejected","reason":str(exc)})
    return {"wave":903,"name":"experiment_chamber","baseline":_digest(baseline),
            "results":results,"executed_external_actions":False,"replayable":True}

def handler(payload:Dict[str,Any]|None=None)->Dict[str,Any]:
    payload=payload or {}
    if payload.get("action","status")=="chamber":
        return chamber(payload.get("events",[]),payload.get("recipes",[]))
    if payload.get("action","status")=="status":
        return {"status":"experimental","wave":903,"name":"experiment_chamber",
                "external_actions":False,"allowed_ops":sorted(ALLOWED_OPS)}
    return {"error":"unknown action","available":["status","chamber"]}

def coherence_vitals()->dict: return {"layer":"experimental","status":"active","wave":"903","module":"experiment_chamber"}
def resonates_with()->list: return ["wave902_hypothesis_forge","wave900_synchronicity_engine","evidence_ledger"]
