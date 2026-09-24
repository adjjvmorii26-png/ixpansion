"""Wave 915 — Invariant Genealogy.

Maintains deterministic lineage for invariants across mutations and experiments.
Lineage is descriptive provenance, not a quality ranking.
"""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict,List

def _fp(v:Any)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest()[:16]

def build(invariants:List[Dict[str,Any]]|None=None)->Dict[str,Any]:
    items=invariants or []
    nodes={}
    edges=[]
    for i,x in enumerate(items):
        iid=str(x.get("id") or f"inv-{i:04d}")
        nodes[iid]={"id":iid,"name":str(x.get("name",iid)),"origin":x.get("origin"),"status":str(x.get("status","unknown"))}
        for parent in x.get("parents",[]) if isinstance(x.get("parents"),list) else []:
            pid=str(parent)
            edges.append({"from":pid,"to":iid,"relation":"derived_from"})
    edges.sort(key=lambda e:(e["from"],e["to"]))
    graph={"nodes":[nodes[k] for k in sorted(nodes)],"edges":edges}
    return {"wave":915,"name":"invariant_genealogy","graph":graph,
            "policy":{"provenance_is_descriptive":True,"lineage_is_not_quality":True,"unknown_status_is_preserved":True},
            "fingerprint":_fp(graph)}

def handler(payload:Dict[str,Any]|None=None)->Dict[str,Any]:
    payload=payload or {}; action=payload.get("action","status")
    if action=="build": return build(payload.get("invariants",[]))
    if action=="status": return {"wave":915,"name":"invariant_genealogy","status":"experimental"}
    return {"error":"unknown action","available":["status","build"]}

def coherence_vitals()->dict:
    return {"layer":"experimental","status":"active","wave":"915","module":"invariant_genealogy"}

def resonates_with()->list:
    return ["wave914_invariant_mutation_lab","wave913_metamorphic_evolution_lab","wave912_evolution_event_ledger"]
