"""Wave 905 — Lineage Graph.

Builds a deterministic directed graph from evidence records. The graph exposes
provenance and evolution without declaring that later nodes are more truthful.
"""
from __future__ import annotations
import hashlib
import json
from typing import Any, Dict, List

def _id(value:Any)->str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest()[:16]

def build(records:List[Dict[str,Any]]|None=None)->Dict[str,Any]:
    records=records or []
    nodes=[]; edges=[]; seen=set()
    for i,r in enumerate(records):
        rid=str(r.get("record_digest") or _id(r))
        if rid in seen: continue
        seen.add(rid)
        nodes.append({"id":rid,"kind":"evidence","wave":r.get("wave",904),
                      "hypothesis":r.get("hypothesis",{}),"falsifier":r.get("falsifier")})
        parent=r.get("parent")
        if parent:
            edges.append({"from":str(parent),"to":rid,"kind":"derived_from"})
    nodes.sort(key=lambda n:n["id"]); edges.sort(key=lambda e:(e["from"],e["to"]))
    roots=sorted(n["id"] for n in nodes if n["id"] not in {e["to"] for e in edges})
    return {"wave":905,"name":"lineage_graph","nodes":nodes,"edges":edges,
            "roots":roots,"node_count":len(nodes),"edge_count":len(edges),
            "replayable":True}

def handler(payload:Dict[str,Any]|None=None)->Dict[str,Any]:
    payload=payload or {}
    if payload.get("action","status")=="build": return build(payload.get("records",[]))
    if payload.get("action","status")=="status":
        return {"status":"experimental","wave":905,"name":"lineage_graph","purpose":"provenance visualization"}
    return {"error":"unknown action","available":["status","build"]}

def coherence_vitals()->dict: return {"layer":"experimental","status":"active","wave":"905","module":"lineage_graph"}
def resonates_with()->list: return ["wave904_evidence_ledger","wave902_hypothesis_forge","evolution_map"]
