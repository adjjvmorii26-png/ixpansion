"""Wave 904 — Evidence Ledger.

Append-only, deterministic records for experimental observations.
The ledger stores provenance and outcome metadata, not mutable conclusions.
"""
from __future__ import annotations
import hashlib
import json
from typing import Any, Dict, List

def _canon(value:Any)->str:
    return json.dumps(value,sort_keys=True,separators=(",",":"),default=str)

def _digest(value:Any)->str:
    return hashlib.sha256(_canon(value).encode()).hexdigest()[:20]

def record(hypothesis:Dict[str,Any], recipe:Dict[str,Any],
           baseline:Any, result:Any, falsifier:Any=None,
           parent:str|None=None)->Dict[str,Any]:
    entry={
        "wave":904,"type":"evidence","hypothesis":dict(hypothesis),
        "recipe":dict(recipe),"baseline_digest":_digest(baseline),
        "result_digest":_digest(result),"falsifier":falsifier,
        "parent":parent,"record_digest":"",
    }
    entry["record_digest"]=_digest(entry)
    return entry

def ledger(records:List[Dict[str,Any]]|None=None)->Dict[str,Any]:
    out=[]; seen=set()
    for raw in records or []:
        item=dict(raw); digest=item.get("record_digest") or _digest({k:v for k,v in item.items() if k!="record_digest"})
        if digest in seen: continue
        item["record_digest"]=digest; seen.add(digest); out.append(item)
    return {"wave":904,"name":"evidence_ledger","records":out,
            "count":len(out),"append_only":True,"replayable":True}

def handler(payload:Dict[str,Any]|None=None)->Dict[str,Any]:
    payload=payload or {}
    action=payload.get("action","status")
    if action=="record":
        return record(payload.get("hypothesis",{}),payload.get("recipe",{}),
                      payload.get("baseline"),payload.get("result"),
                      payload.get("falsifier"),payload.get("parent"))
    if action=="ledger": return ledger(payload.get("records",[]))
    if action=="status": return {"status":"experimental","wave":904,"name":"evidence_ledger","append_only":True}
    return {"error":"unknown action","available":["status","record","ledger"]}

def coherence_vitals()->dict: return {"layer":"experimental","status":"active","wave":"904","module":"evidence_ledger"}
def resonates_with()->list: return ["wave902_hypothesis_forge","wave903_experiment_chamber","lineage_graph"]
