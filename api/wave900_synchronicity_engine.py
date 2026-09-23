"""Wave 900 — Synchronicity Engine.

An experimental serendipity layer for IXpansion. It creates deterministic,
inspectable coincidence fields from events already supplied by the caller.
It detects affinity without claiming causation.
"""
from __future__ import annotations
import hashlib
import re
from typing import Any, Dict, List

TOKEN_RE = re.compile(r"[a-z0-9_]{3,}", re.I)

def _tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall((text or "").lower()))

def _fingerprint(event: Dict[str, Any]) -> str:
    raw = "|".join([str(event.get("id","")), str(event.get("title","")),
                    str(event.get("text","")), str(event.get("realm",""))])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

def _affinity(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    ta = _tokens(f"{a.get('title','')} {a.get('text','')}")
    tb = _tokens(f"{b.get('title','')} {b.get('text','')}")
    if not ta or not tb:
        return 0.0
    jaccard = len(ta & tb) / len(ta | tb)
    realm = 0.12 if a.get("realm") and a.get("realm") == b.get("realm") else 0.0
    return round(min(1.0, jaccard + realm), 4)

def field(events: List[Dict[str, Any]], threshold: float = 0.08) -> Dict[str, Any]:
    clean = []
    for i, event in enumerate(events or []):
        item = dict(event)
        item.setdefault("id", f"event-{i+1}")
        item["fingerprint"] = _fingerprint(item)
        clean.append(item)
    collisions = []
    for i, a in enumerate(clean):
        for b in clean[i+1:]:
            score = _affinity(a, b)
            if score >= threshold:
                collisions.append({
                    "a": a["id"], "b": b["id"], "affinity": score,
                    "shared_tokens": sorted(
                        _tokens(f"{a.get('title','')} {a.get('text','')}") &
                        _tokens(f"{b.get('title','')} {b.get('text','')}")
                    )[:12],
                })
    collisions.sort(key=lambda x: (-x["affinity"], x["a"], x["b"]))
    energy = round(sum(c["affinity"] for c in collisions), 4)
    return {"wave":900, "name":"synchronicity_engine", "events":clean,
            "collisions":collisions, "energy":energy,
            "phase":"quiet" if energy == 0 else ("spark" if energy < 1 else "storm"),
            "replayable":True}

def handler(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action", "status")
    if action == "field":
        return field(payload.get("events", []), float(payload.get("threshold", 0.08)))
    if action == "status":
        return {"status":"experimental","wave":900,"name":"synchronicity_engine",
                "principle":"detect inspectable coincidence without claiming causation"}
    return {"error":f"unknown action: {action}","available":["status","field"]}

def coherence_vitals() -> dict:
    return {"layer":"experimental","status":"active","wave":"900","module":"synchronicity_engine"}

def resonates_with() -> list:
    return ["semantic_loom","echo_stratigraphy","dream_synthesis","resonance_ledger"]
