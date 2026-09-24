"""Wave 911 — Temporal Repository Diff.

Compares two normalized repository snapshots and classifies structural change.
Classification is descriptive: change is not treated as regression.
"""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict,List

def _fp(v:Any)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest()[:16]

def _norm(files:List[Dict[str,Any]])->Dict[str,Dict[str,Any]]:
    return {str(x["path"]):{"path":str(x["path"]),"size":int(x.get("size",0) or 0),"category":str(x.get("category",""))} for x in files if x.get("path")}

def build(before:List[Dict[str,Any]]|None=None,after:List[Dict[str,Any]]|None=None)->Dict[str,Any]:
    a,b=_norm(before or []),_norm(after or [])
    added=sorted(set(b)-set(a)); removed=sorted(set(a)-set(b))
    changed=sorted(p for p in set(a)&set(b) if a[p]!=b[p])
    records=[]
    for p in added: records.append({"path":p,"kind":"added","status":"changed"})
    for p in removed: records.append({"path":p,"kind":"removed","status":"changed"})
    for p in changed: records.append({"path":p,"kind":"modified","before":a[p],"after":b[p],"status":"changed"})
    records.sort(key=lambda x:(x["path"],x["kind"]))
    summary={"added":len(added),"removed":len(removed),"modified":len(changed)}
    return {"wave":911,"name":"temporal_repository_diff","before_fingerprint":_fp(a),"after_fingerprint":_fp(b),"summary":summary,"changes":records,"policy":{"change_is_not_regression":True,"classification_is_descriptive":True,"semantic_behavior_not_inferred":True},"fingerprint":_fp({"before":a,"after":b,"changes":records})}

def handler(payload:Dict[str,Any]|None=None)->Dict[str,Any]:
    payload=payload or {}
    if payload.get("action","status")=="build": return build(payload.get("before",[]),payload.get("after",[]))
    if payload.get("action","status")=="status": return {"wave":911,"name":"temporal_repository_diff","status":"experimental"}
    return {"error":"unknown action","available":["status","build"]}

def coherence_vitals()->dict:
    return {"layer":"experimental","status":"active","wave":"911","module":"temporal_repository_diff"}

def resonates_with()->list:
    return ["wave909_repository_observatory","wave910_repository_evidence_graph","wave908_topology_integrity"]
