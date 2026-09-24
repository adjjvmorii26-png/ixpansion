"""Wave 906 — Evolution Map.

Describes structural patterns in a lineage graph without ranking branches.
"""
from __future__ import annotations
import hashlib, json
from typing import Any, Dict, List

def _digest(value: Any) -> str:
    raw=json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def build(records: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    records=records or []
    by_id={}
    for r in records:
        rid=str(r.get("record_digest") or _digest(r))
        by_id.setdefault(rid,r)
    ids=sorted(by_id)
    parents={rid: str(r.get("parent")) for rid,r in by_id.items() if r.get("parent")}
    children={rid:[] for rid in ids}
    for child,parent in parents.items():
        children.setdefault(parent,[]).append(child)
    for v in children.values(): v.sort()
    roots=sorted(rid for rid in ids if rid not in set(parents))
    leaves=sorted(rid for rid in ids if not children.get(rid))
    divergence=sorted({"node":rid,"children":len(children[rid])} for rid in ids if len(children[rid])>1,
                      key=lambda x:x["node"])
    convergence=[]
    for rid in ids:
        incoming=[p for c,p in parents.items() if c==rid]
        if len(incoming)>1: convergence.append({"node":rid,"parents":sorted(incoming)})
    signatures={}
    for rid,r in by_id.items():
        sig=_digest({"hypothesis":r.get("hypothesis"),"recipe":r.get("recipe")})
        signatures.setdefault(sig,[]).append(rid)
    motifs=[{"signature":s,"nodes":sorted(ns)} for s,ns in signatures.items() if len(ns)>1]
    orphan_parents=sorted(p for p in parents.values() if p not in by_id)
    return {"wave":906,"name":"evolution_map","node_count":len(ids),
            "edge_count":len(parents),"roots":roots,"leaves":leaves,
            "divergence":divergence,"convergence":convergence,
            "repeated_motifs":sorted(motifs,key=lambda x:x["signature"]),
            "orphan_parents":orphan_parents,"replayable":True}

def handler(payload: Dict[str,Any] | None=None) -> Dict[str,Any]:
    payload=payload or {}
    if payload.get("action","status")=="build": return build(payload.get("records",[]))
    if payload.get("action","status")=="status":
        return {"status":"experimental","wave":906,"name":"evolution_map",
                "purpose":"descriptive lineage structure"}
    return {"error":"unknown action","available":["status","build"]}

def coherence_vitals()->dict:
    return {"layer":"experimental","status":"active","wave":"906","module":"evolution_map"}

def resonates_with()->list:
    return ["wave905_lineage_graph","wave904_evidence_ledger","wave907_branch_atlas"]
