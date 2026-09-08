"""Wave 516: Module Search — organic search across all organism modules."""
from __future__ import annotations
import importlib, os, time
from typing import Any, Dict, List

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    payload = payload or {}
    query = payload.get("q", payload.get("query", "")).strip().lower()
    if not query:
        return {"action": "search", "query": "", "results": [], "hint": "Use ?q=<search_term> to search modules"}
    from api.coherence_regulator import KNOWN_LIVING_MODULES
    matches = []
    for name in KNOWN_LIVING_MODULES:
        if query in name:
            matches.append({"module": name, "type": "name_match"})
        else:
            # Check docstring
            try:
                mod = importlib.import_module(f"api.{name}")
                doc = (mod.__doc__ or "").lower()
                if query in doc:
                    matches.append({"module": name, "type": "doc_match", "snippet": (mod.__doc__ or "")[:150]})
            except Exception:
                pass
    matches.sort(key=lambda m: 0 if m["type"] == "name_match" else 1)
    return {
        "action": "search",
        "query": query,
        "results": matches[:30],
        "total_matches": len(matches),
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
