"""Wave 922 — Integrity Ledger.

Appends immutable-style integrity observations to an ordered, deterministic
ledger. This records fingerprints and provenance without asserting correctness.
"""
from __future__ import annotations
import hashlib, json
from typing import Any, Dict, List

def _digest(value: Any) -> str:
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def append(entries: List[Dict[str, Any]]|None=None, observation: Dict[str, Any]|None=None)->Dict[str, Any]:
    ledger=[dict(x) for x in (entries or [])]
    item=dict(observation or {})
    if not item.get("fingerprint"):
        raise ValueError("fingerprint is required")
    if not item.get("source"):
        raise ValueError("source is required")
    item["sequence"]=len(ledger)
    ledger.append(item)
    return {"wave":922,"name":"integrity_ledger","entries":ledger,
            "ledger_digest":_digest(ledger),
            "policy":{"ordered":True,"provenance_required":True,"no_truth_inference":True}}

def verify(ledger: Dict[str, Any])->Dict[str, Any]:
    entries=list(ledger.get("entries") or [])
    return {"entry_count":len(entries),
            "sequences":[x.get("sequence") for x in entries],
            "contiguous": [x.get("sequence") for x in entries]==list(range(len(entries))),
            "ledger_digest":_digest(entries)}

def handler(payload: Dict[str, Any]|None=None)->Dict[str, Any]:
    payload=payload or {}; action=payload.get("action","status")
    if action=="append": return append(payload.get("entries",[]),payload.get("observation"))
    if action=="verify": return verify(payload.get("ledger",{}))
    if action=="status": return {"wave":922,"name":"integrity_ledger","status":"experimental"}
    return {"error":"unknown action","available":["status","append","verify"]}

def coherence_vitals()->dict:
    return {"layer":"experimental","status":"active","wave":"922","module":"integrity_ledger"}

def resonates_with()->list:
    return ["wave921_replay_integrity","wave920_memory_replay"]
