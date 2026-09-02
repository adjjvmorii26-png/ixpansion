"""Wave 216 — The Organism Bridges: Knot Weaver.

Takes an untouched interstice bridge and WEAVES it: creates a
binding contract between the repo and the organ — a proposed
file, a route, or a ritual that would make the connection real.
The weaver tracks which bridges have been proposed, tied, or
left loose, so the organism can measure progress on its own
cross-project architecture.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List

_WEAVES: List[Dict[str, Any]] = []


def _knot_id(repo: str, organ: str) -> str:
    raw = f"{repo}::{organ}"
    return "KNOT-" + hashlib.sha256(raw.encode()).hexdigest()[:8].upper()


def _pattern(repo: str, organ: str) -> str:
    options = [
        f"{repo}/bridges/{organ}_probe.py",
        f"{repo}/interfaces/{organ}_port.py",
        f"{repo}/rituals/{organ}_handshake.md",
    ]
    return options[len(_WEAVES) % len(options)]


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "bridge", "status": "stable", "resonance": 0.76, "wave": 216}


def resonates_with() -> list:
    return ["knot", "weave", "tie", "bind", "contract", "bridge", "connect"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "loom")

    if action == "loom":
        return {"weaves": _WEAVES, "count": len(_WEAVES)}

    if action == "weave":
        repo = payload.get("repo")
        organ = payload.get("organ")
        if not repo or not organ:
            return {"status": "error", "error": "repo and organ required"}
        weave = {
            "id": _knot_id(repo, organ),
            "repo": repo,
            "organ": organ,
            "pattern": _pattern(repo, organ),
            "state": "proposed",
            "made_at": round(time.time(), 2),
        }
        _WEAVES.append(weave)
        return {"status": "woven", "weave": weave}

    if action == "tie":
        kid = payload.get("id")
        if not kid:
            return {"status": "error", "error": "knot id required"}
        for w in _WEAVES:
            if w["id"] == kid.upper():
                w["state"] = "tied"
                return {"status": "tied", "weave": w}
        return {"status": "not_found"}

    return {"status": "active", "weave_count": len(_WEAVES)}
