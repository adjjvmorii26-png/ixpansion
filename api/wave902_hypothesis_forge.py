"""Wave 902 — Hypothesis Forge.

Turns observed field structure into bounded, reproducible experiment proposals.
It never executes proposals; it only produces candidates with explicit inputs,
expected observations, and falsification checks.
"""
from __future__ import annotations
import hashlib
from typing import Any, Dict, List

def _seed(events: List[Dict[str,Any]], trajectory: List[Dict[str,Any]]) -> str:
    raw=repr(sorted((str(e.get("id","")),str(e.get("fingerprint",""))) for e in events))
    raw+=repr(trajectory[-8:])
    return hashlib.sha256(raw.encode()).hexdigest()

def forge(events: List[Dict[str,Any]]|None=None, trajectory: List[Dict[str,Any]]|None=None, limit:int=3)->Dict[str,Any]:
    events=events or []; trajectory=trajectory or []; limit=max(1,min(int(limit),8))
    seed=_seed(events,trajectory)
    recurring=len({round(float(p.get("x",0)),2) for p in trajectory[-12:]}) < max(3,len(trajectory[-12:])//2) if trajectory else False
    ideas=[
      {"id":"H902-A","question":"Does repeated semantic overlap persist when event order is permuted?",
       "method":"shuffle event order while preserving event content","observation":"compare collision sets and energy",
       "falsifier":"material change beyond configured tolerance"},
      {"id":"H902-B","question":"Does the attractor trajectory retain structure when one signal is removed?",
       "method":"leave-one-event-out replay","observation":"compare trajectory spread and recurrence",
       "falsifier":"structure disappears for every removal"},
      {"id":"H902-C","question":"Are apparent recurring states robust to small fingerprint perturbations?",
       "method":"apply deterministic one-bit seed perturbations","observation":"measure recurrence overlap",
       "falsifier":"recurrence is absent across all perturbations"},
      {"id":"H902-D","question":"Can a quiet field become a spark through composition alone?",
       "method":"combine two independently quiet event sets","observation":"measure resulting field energy",
       "falsifier":"combined energy remains indistinguishable from baseline"},
    ]
    if recurring: ideas.insert(0,{"id":"H902-R","question":"Is the observed recurrence a stable basin or a short-lived artifact?",
      "method":"extend trajectory 8x with identical seed","observation":"compare late-state occupancy",
      "falsifier":"recurrence vanishes immediately"})
    return {"wave":902,"name":"hypothesis_forge","seed":seed[:16],"proposals":ideas[:limit],"executable":False,"replayable":True}

def handler(payload:Dict[str,Any]|None=None)->Dict[str,Any]:
    payload=payload or {}
    if payload.get("action","status")=="forge": return forge(payload.get("events"),payload.get("trajectory"),payload.get("limit",3))
    if payload.get("action","status")=="status": return {"status":"experimental","wave":902,"name":"hypothesis_forge","executable":False}
    return {"error":"unknown action","available":["status","forge"]}

def coherence_vitals()->dict: return {"layer":"experimental","status":"active","wave":"902","module":"hypothesis_forge"}
def resonates_with()->list: return ["wave900_synchronicity_engine","wave901_strange_attractor","experiment_registry"]
