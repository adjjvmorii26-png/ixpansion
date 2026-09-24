"""Wave 913 — Metamorphic Evolution Lab.

Runs deterministic transformations over a supplied snapshot and checks declared
invariants. Outcomes are observational; a violation is not itself proof of a
regression.
"""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict,List

def _fp(v:Any)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest()[:16]

def _files(snapshot:List[Dict[str,Any]])->List[Dict[str,Any]]:
    return sorted(
        [{"path":str(x["path"]),"size":int(x.get("size",0) or 0),"category":str(x.get("category",""))}
         for x in snapshot if x.get("path")],
        key=lambda x:x["path"])

def identity(snapshot:List[Dict[str,Any]])->List[Dict[str,Any]]:
    return _files(snapshot)

def reorder(snapshot:List[Dict[str,Any]])->List[Dict[str,Any]]:
    return list(reversed(_files(snapshot)))

TRANSFORMS={"identity":identity,"reorder":reorder}

def check_invariants(before:List[Dict[str,Any]],after:List[Dict[str,Any]],invariants:List[str])->List[Dict[str,Any]]:
    b=_files(before); a=_files(after); results=[]
    for inv in sorted(set(invariants)):
        if inv=="file_set_preserved":
            ok={x["path"] for x in b}=={x["path"] for x in a}
        elif inv=="fingerprint_preserved":
            ok=_fp(b)==_fp(a)
        else:
            results.append({"invariant":inv,"outcome":"unknown"}); continue
        results.append({"invariant":inv,"outcome":"preserved" if ok else "violated"})
    return results

def run(snapshot:List[Dict[str,Any]]|None=None,transformations:List[str]|None=None,invariants:List[str]|None=None)->Dict[str,Any]:
    snapshot=snapshot or []; transformations=transformations or ["identity"]; invariants=invariants or ["file_set_preserved"]
    events=[]
    for name in transformations:
        fn=TRANSFORMS.get(name)
        if not fn:
            events.append({"transformation":name,"outcome":"unknown","reason":"unsupported_transform"})
            continue
        after=fn(snapshot)
        checks=check_invariants(snapshot,after,invariants)
        events.append({"transformation":name,"before_fingerprint":_fp(_files(snapshot)),"after_fingerprint":_fp(_files(after)),"checks":checks})
    return {"wave":913,"name":"metamorphic_evolution_lab","events":events,"policy":{"observations_are_not_regressions":True,"unknown_is_preserved":True,"invariants_must_be_declared":True},"fingerprint":_fp(events)}

def handler(payload:Dict[str,Any]|None=None)->Dict[str,Any]:
    payload=payload or {}; action=payload.get("action","status")
    if action=="run": return run(payload.get("snapshot",[]),payload.get("transformations"),payload.get("invariants"))
    if action=="status": return {"wave":913,"name":"metamorphic_evolution_lab","status":"experimental"}
    return {"error":"unknown action","available":["status","run"]}

def coherence_vitals()->dict:
    return {"layer":"experimental","status":"active","wave":"913","module":"metamorphic_evolution_lab"}

def resonates_with()->list:
    return ["wave912_evolution_event_ledger","wave911_temporal_repository_diff","wave910_repository_evidence_graph"]
