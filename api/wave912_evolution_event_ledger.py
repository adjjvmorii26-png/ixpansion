"""Wave 912 — Evolution Event Ledger.

Turns temporal changes plus optional provenance into deterministic, append-only
architectural events. It records classification without deciding whether a
change is good or bad.
"""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict,List

def _fp(v:Any)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest()[:16]

def build(changes:List[Dict[str,Any]]|None=None,evidence:List[Dict[str,Any]]|None=None)->Dict[str,Any]:
    changes=changes or []; evidence=evidence or []
    evidence_by_id={str(x.get("id")):x for x in evidence if x.get("id") is not None}
    events=[]
    for i,c in enumerate(changes):
        ids=[str(x) for x in c.get("evidence_ids",[]) if str(x) in evidence_by_id]
        event={
            "id":str(c.get("id") or f"event-{i:04d}"),
            "path":str(c.get("path","")),
            "kind":str(c.get("kind","unknown")),
            "classification":str(c.get("classification","unexplained")),
            "evidence_ids":sorted(ids),
        }
        events.append(event)
    events.sort(key=lambda x:x["id"])
    return {
        "wave":912,
        "name":"evolution_event_ledger",
        "events":events,
        "summary":{"events":len(events),"with_evidence":sum(bool(x["evidence_ids"]) for x in events)},
        "policy":{
            "append_only":True,
            "classification_is_descriptive":True,
            "unexplained_is_not_regression":True,
            "evidence_is_not_truth":True,
        },
        "fingerprint":_fp(events),
    }

def handler(payload:Dict[str,Any]|None=None)->Dict[str,Any]:
    payload=payload or {}
    if payload.get("action","status")=="build":
        return build(payload.get("changes",[]),payload.get("evidence",[]))
    if payload.get("action","status")=="status":
        return {"wave":912,"name":"evolution_event_ledger","status":"experimental"}
    return {"error":"unknown action","available":["status","build"]}

def coherence_vitals()->dict:
    return {"layer":"experimental","status":"active","wave":"912","module":"evolution_event_ledger"}

def resonates_with()->list:
    return ["wave911_temporal_repository_diff","wave910_repository_evidence_graph","wave909_repository_observatory"]
