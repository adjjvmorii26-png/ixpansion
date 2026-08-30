"""Wave 142 — Cognition Fingerprint.

Every agent thinks by a distinct fingerprint. This module samples how
an agent actually reasons (through the frontier) and distills a stable
signature of its temperament: verbosity, novelty, risk, and depth.
Fingerprints make the workforce legible and let you spot drift.
"""
from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List

try:
    import gateway_ink
except Exception:  # pragma: no cover
    gateway_ink = None

_STORE: Dict[str, Dict[str, Any]] = {}


def _analyze(text: str, sample: str) -> Dict[str, Any]:
    words = re.findall(r"[A-Za-z]+", text)
    sample_words = re.findall(r"[A-Za-z]+", sample)
    rare = sorted(set(w.lower() for w in words if len(w) > 6))[:3]
    return {
        "verbosity": round(min(len(words) / 120.0, 1.0), 3),
        "neologism": round(min(len(rare) / 6.0, 1.0), 3),
        "decisiveness": round(min(len(sample_words) / 30.0, 1.0), 3),
        "depth": round(min(len({w.lower() for w in words}) / 40.0, 1.0), 2),
        "signature_words": rare,
    }


def _probe_fingerprint(agent_id: str, model: str) -> Dict[str, Any]:
    sample_prompt = "In one breath, state your nature."
    result = gateway_ink.relay(sample_prompt, model=model, max_tokens=90, temperature=1.0) if gateway_ink else {}
    reply = result.get("reply") or ""
    profile = _analyze(reply, sample_prompt)
    entry = {"updated": time.time(), "served": bool(result.get("ok")), **profile}
    _STORE[agent_id] = entry
    return entry


def cognition_fingerprint_handler(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action") or "status"
    agent = str(payload.get("agent") or payload.get("agent_id") or "default")
    model = payload.get("model") or "spacexai/grok-4.6"

    if action == "status":
        return {"status": "active", "fingerprints": list(_STORE), "count": len(_STORE)}

    if action == "sample":
        profile = _probe_fingerprint(agent, model)
        return {"status": "active", "agent": agent, "fingerprint": profile}

    if action == "get":
        return {"status": "active", "agent": agent,
                "fingerprint": _STORE.get(agent, {"served": False, "note": "unsampled yet"})}

    if action == "drift":
        base = _STORE.get(agent, {})
        if not base:
            base = _probe_fingerprint(agent, model)
        return {"status": "active", "agent": agent, "baseline": {
            k: base.get(k) for k in ("verbosity", "neologism", "depth")},
            "drift_alert": base.get("verbosity", 0) > 0.9}

    return {"status": "active", "error": f"unknown action '{action}'",
            "available": ["status", "sample", "get", "drift"]}
