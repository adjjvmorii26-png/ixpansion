"""Wave 916 — Evolution Memory.

Stores reusable experimental observations with provenance and uncertainty intact.
Memory is retrieval context, not truth.
"""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict,List

def _fp(v:Any)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest()[:16]

def build(observations:List[Dict[str,Any]]|None=None)->Dict[str,Any]:
    items=observations or []; memories=[]
    for i,x in enumerate(items):
        source=x.get("source")
        if source is None or str(source).strip()=="":
            raise ValueError("source is required for experimental memory provenance")
        memories.append({
            "id":str(x.get("id") or f"memory-{i:04d}"),
            "kind":str(x.get("kind","observation")),
            "content":x.get("content"),
            "status":str(x.get("status","unknown")),
            "source":source,
            "lineage":sorted(str(v) for v in (x.get("lineage") or [])),
        })
    memories.sort(key=lambda x:x["id"])
    return {"wave":916,"name":"evolution_memory","memories":memories,
            "policy":{"memory_is_context_not_truth":True,"provenance_is_required":True,"uncertainty_is_preserved":True},
            "fingerprint":_fp(memories)}

def recall(memory:Dict[str,Any],query:str)->Dict[str,Any]:
    q=str(query).lower()
    content=str(memory.get("content","")).lower()
    return {
        "match":q in content,
        "memory_id":memory.get("id"),
        "query":query,
        "status":memory.get("status","unknown"),
        "source":memory.get("source"),
        "lineage":list(memory.get("lineage") or []),
    }

def handler(payload:Dict[str,Any]|None=None)->Dict[str,Any]:
    payload=payload or {}; action=payload.get("action","status")
    if action=="build": return build(payload.get("observations",[]))
    if action=="recall": return recall(payload.get("memory",{}),str(payload.get("query","")))
    if action=="status": return {"wave":916,"name":"evolution_memory","status":"experimental"}
    return {"error":"unknown action","available":["status","build","recall"]}

def coherence_vitals()->dict:
    return {"layer":"experimental","status":"active","wave":"916","module":"evolution_memory"}

def resonates_with()->list:
    return ["wave915_invariant_genealogy","wave914_invariant_mutation_lab","wave912_evolution_event_ledger"]
