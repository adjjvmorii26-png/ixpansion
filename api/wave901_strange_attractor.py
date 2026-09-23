"""Wave 901 — Strange Attractor.

Turns repeated synchronicity fields into a tiny deterministic dynamical system.
The attractor is descriptive: it visualizes recurring states; it does not
claim that the system predicts real-world events.
"""
from __future__ import annotations
import hashlib
import math
from typing import Any, Dict, List

def _unit(seed: str) -> float:
    return int(hashlib.sha256(seed.encode()).hexdigest()[:12],16) / float(16**12-1)

def attract(events: List[Dict[str,Any]], steps: int = 24) -> Dict[str,Any]:
    steps=max(1,min(int(steps),256))
    state=[0.173,0.417,0.731]
    history=[]
    for i in range(steps):
        payload="|".join(sorted(str(e.get("fingerprint",e.get("id",i))) for e in (events or [])))
        jitter=_unit(payload+":"+str(i))
        x,y,z=state
        # Bounded nonlinear recurrence: reproducible, inexpensive, inspectable.
        state=[
            (math.sin(3.71*y+0.31*jitter)+1)/2,
            (math.sin(4.13*z+0.17*jitter)+1)/2,
            (math.sin(3.47*x+0.23*jitter)+1)/2,
        ]
        history.append({"step":i+1,"x":round(state[0],6),"y":round(state[1],6),"z":round(state[2],6)})
    spread=round(sum(abs(history[i]["x"]-history[i-1]["x"]) for i in range(1,len(history))),6) if history else 0
    return {"wave":901,"name":"strange_attractor","steps":steps,"trajectory":history,
            "spread":spread,"replayable":True}

def handler(payload: Dict[str,Any]|None=None)->Dict[str,Any]:
    payload=payload or {}
    if payload.get("action","status")=="attract":
        return attract(payload.get("events",[]),payload.get("steps",24))
    if payload.get("action","status")=="status":
        return {"status":"experimental","wave":901,"name":"strange_attractor",
                "principle":"visualize recurring nonlinear states without claiming prediction"}
    return {"error":"unknown action","available":["status","attract"]}

def coherence_vitals()->dict:
    return {"layer":"experimental","status":"active","wave":"901","module":"strange_attractor"}

def resonates_with()->list:
    return ["wave900_synchronicity_engine","entropy_heatmap","temporal_field","resonance_mapper"]
