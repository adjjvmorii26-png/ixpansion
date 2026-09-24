"""Wave 910 — Repository Evidence Graph.

Turns repository observations into a small provenance graph. Claims remain
claims: the graph never promotes an observation into semantic truth.
"""
from __future__ import annotations
import hashlib, json
from typing import Any, Dict, List

def _fp(value: Any) -> str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest()[:16]

def build(observations: List[Dict[str,Any]]|None=None) -> Dict[str,Any]:
    observations=observations or []
    nodes={}
    edges=[]
    for i,obs in enumerate(observations):
        claim=str(obs.get("claim") or f"observation:{i}")
        oid=str(obs.get("id") or _fp(obs))
        nodes[oid]={"id":oid,"type":"observation","claim":claim,"status":str(obs.get("status") or "observed")}
        for evidence in obs.get("evidence",[]) if isinstance(obs.get("evidence"),list) else []:
            eid=str(evidence.get("id") if isinstance(evidence,dict) else evidence)
            if not eid: continue
            nodes.setdefault(eid,{"id":eid,"type":"evidence"})
            edges.append({"from":oid,"to":eid,"relation":"supported_by"})
    edges.sort(key=lambda x:(x["from"],x["to"],x["relation"]))
    ordered=[nodes[k] for k in sorted(nodes)]
    graph={"nodes":ordered,"edges":edges}
    return {"wave":910,"name":"repository_evidence_graph","graph":graph,
            "node_count":len(ordered),"edge_count":len(edges),
            "fingerprint":_fp(graph),"policy":{"claims_are_not_truth":True,"provenance_is_explicit":True,"conflicts_are_preserved":True}}

def handler(payload:Dict[str,Any]|None=None)->Dict[str,Any]:
    payload=payload or {}
    if payload.get("action","status")=="build": return build(payload.get("observations",[]))
    if payload.get("action","status")=="status":
        return {"wave":910,"name":"repository_evidence_graph","status":"experimental"}
    return {"error":"unknown action","available":["status","build"]}

def coherence_vitals()->dict:
    return {"layer":"experimental","status":"active","wave":"910","module":"repository_evidence_graph"}

def resonates_with()->list:
    return ["wave909_repository_observatory","wave908_topology_integrity","wave906_evolution_map"]
