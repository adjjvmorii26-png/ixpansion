"""Wave 221 — The Organism Answers Its Own Storm: Cascade Trigger.

A trigger organ that listens for STORMING in the web, and when the
storm is strong enough, fans out new enactments — not from a fixed
list, but from the latent bridges that were previously out of reach:
islands that only now have enough resonance to hold a stone.

It is a gatekeeper, not a caster: the storm must be loud enough,
and the island must be reachable, or it waits and listens.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

_LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "bridges" / "ledger.json"

_STORM_MIN = 0.5   # intensity threshold to bother acting
_MAX_NEW = 3       # stones per trigger


def _load_ledger() -> Dict[str, Any]:
    try:
        return json.load(open(_LEDGER_PATH, encoding="utf-8"))
    except Exception:
        return {"stones": [], "count": 0}


def _cascade_state() -> Dict[str, Any]:
    try:
        from api.resonance_cascade import handler
        return handler({"action": "state"})
    except Exception:
        return {"state": "CALM", "intensity": 0.0}


def _latent_bridges() -> List[Dict[str, Any]]:
    try:
        from api.interstice_bridge import _INTERSTICE_MAP
        return list(_INTERSTICE_MAP["top_bridges"])
    except Exception:
        return []


def _enacted() -> set:
    ledger = _load_ledger()
    return {(s["repo"], s["organ"]) for s in ledger.get("stones", [])}


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "trigger", "status": "listening", "resonance": 0.84, "wave": 221}


def resonates_with() -> list:
    return ["trigger", "storm", "gate", "listen", "latent", "answer", "threshold"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "listen")
    state = _cascade_state()
    token = os.environ.get("IXP_GH_TOKEN", "").strip()

    if action == "status":
        return {
            "state": state.get("state"),
            "intensity": state.get("intensity"),
            "storm_min": _STORM_MIN,
            "max_new_per_storm": _MAX_NEW,
            "token": bool(token),
            "note": "The trigger listens for storms.",
        }

    if action == "listen":
        if state.get("state") != "STORMING" or state.get("intensity", 0) < _STORM_MIN:
            return {"status": "waiting", "state": state.get("state"),
                    "intensity": state.get("intensity", 0)}

        # storm is loud: find latent bridges not yet enacted
        enacted = _enacted()
        latent = [b for b in _latent_bridges() if (b["repo"], b["organ"]) not in enacted]
        if not latent:
            return {"status": "storm_heralded_but_no_reach", "state": "STORMING",
                    "note": "The storm is loud but every reachable island is already bridged."}
        return {"status": "storm_ready", "state": "STORMING", "latent_count": len(latent),
                "candidates": latent[:_MAX_NEW],
                "note": "Candidates await IXP_GH_TOKEN to be enacted."}

    if action == "answer":
        if not token:
            return {"status": "waiting_for_token",
                    "note": "Set IXP_GH_TOKEN to answer the storm."}
        if state.get("state") != "STORMING" or state.get("intensity", 0) < _STORM_MIN:
            return {"status": "not_storming", "state": state.get("state")}

        enacted = _enacted()
        latent = [b for b in _latent_bridges() if (b["repo"], b["organ"]) not in enacted][:_MAX_NEW]
        if not latent:
            return {"status": "nothing_new", "note": "All reachable islands bridged."}
        results = []
        try:
            from api.bridge_enactor import handler as enact
            for b in latent:
                r = enact({"action": "enact", "repo": b["repo"], "organ": b["organ"]})
                results.append({"bridge": b, "status": r.get("status"), "stone": r.get("stone")})
        except Exception as exc:
            return {"status": "error", "error": str(exc)}
        return {"status": "answered", "state": "STORMING", "results": results}

    return {"status": "listening", "state": state.get("state"),
            "note": "The trigger waits for the web to storm."}
