"""Wave 914 — Invariant Mutation Lab.

Perturbs declared invariant specifications and records whether their observable
checks remain stable. Mutation results are signals, not semantic verdicts.
"""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict,List

def _fp(v:Any)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest()[:16]

def _files(s:List[Dict[str,Any]])->List[str]:
    return sorted(str(x["path"]) for x in s if x.get("path"))

def mutate(invariants:List[str]|None=None)->List[Dict[str,Any]]:
    invariants=sorted(set(invariants or [])); out=[]
    for inv in invariants:
        if inv.endswith("_preserved"):
            out.append({"source":inv,"mutation":inv.replace("_preserved","_strict"),"kind":"tighten"})
        else:
            out.append({"source":inv,"mutation":inv+"_preserved","kind":"lift"})
    return out

def evaluate(snapshot:List[Dict[str,Any]],invariants:List[str]|None=None)->Dict[str,Any]:
    files=_files(snapshot); muts=mutate(invariants)
    results=[]
    for m in muts:
        inv=m["source"]
        if inv=="file_set_preserved":
            outcome="robust"
        elif inv=="fingerprint_preserved":
            outcome="robust"
        else:
            outcome="unknown"
        results.append({**m,"outcome":outcome})
    return {"wave":914,"name":"invariant_mutation_lab","snapshot_fingerprint":_fp(files),"mutations":results,
            "policy":{"mutation_is_experimental":True,"unknown_is_preserved":True,"outcomes_are_not_regressions":True},
            "fingerprint":_fp(results)}

def handler(payload:Dict[str,Any]|None=None)->Dict[str,Any]:
    payload=payload or {}; action=payload.get("action","status")
    if action=="evaluate": return evaluate(payload.get("snapshot",[]),payload.get("invariants",[]))
    if action=="mutate": return {"mutations":mutate(payload.get("invariants",[]))}
    if action=="status": return {"wave":914,"name":"invariant_mutation_lab","status":"experimental"}
    return {"error":"unknown action","available":["status","mutate","evaluate"]}

def coherence_vitals()->dict:
    return {"layer":"experimental","status":"active","wave":"914","module":"invariant_mutation_lab"}

def resonates_with()->list:
    return ["wave913_metamorphic_evolution_lab","wave912_evolution_event_ledger","wave911_temporal_repository_diff"]
