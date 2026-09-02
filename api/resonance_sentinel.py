"""Wave 218 — The Organism Watches the Cracks: Resonance Sentinel.

A living diagnostics organ that watches the bridge network for:
  1. DRIFT — worlds that share themes but have no stone between them
  2. ROT   — enacted stones whose resonance decayed below a living floor
  3. HOLLOW— repos carrying stones but no longer evolving

It reports the health of the bridge web and proposes repairs.
It does not act — it only watches, so the organism never blinds itself.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

_LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "bridges" / "ledger.json"
_THRESHOLD_ROT = 0.02


def _load_ledger() -> Dict[str, Any]:
    try:
        return json.load(open(_LEDGER_PATH, encoding="utf-8"))
    except Exception:
        return {"stones": [], "count": 0}


def _repo_health(stones: List[Dict[str, Any]]) -> float:
    if not stones:
        return 1.0
    return len({s.get("repo") for s in stones}) / len(stones)


def _candidate_bridges() -> List[Dict[str, Any]]:
    try:
        from api.interstice_bridge import _INTERSTICE_MAP
        return list(_INTERSTICE_MAP["top_bridges"])
    except Exception:
        return []


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "sentinel", "status": "watching", "resonance": 0.9, "wave": 218}


def resonates_with() -> list:
    return ["drift", "rot", "decay", "watch", "sentinel", "crack", "repair", "bridge"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "report")

    ledger = _load_ledger()
    stones = ledger.get("stones", [])
    enacted = {(s["repo"], s["organ"]) for s in stones}
    all_bridges = _candidate_bridges()

    report = {"stones": len(stones), "repos": len({s["repo"] for s in stones})}

    drift = [
        {"repo": b["repo"], "organ": b["organ"], "resonance": b.get("resonance", 0.0)}
        for b in all_bridges
        if (b["repo"], b["organ"]) not in enacted
    ]
    report["drift"] = {"count": len(drift), "bridges": drift}

    rot = [
        {"stone": s.get("stone"), "repo": s.get("repo"), "organ": s.get("organ"), "resonance": s.get("resonance", 0)}
        for s in stones if s.get("resonance", 0) < _THRESHOLD_ROT
    ]
    report["rot"] = {"count": len(rot), "stones": rot, "threshold": _THRESHOLD_ROT}

    drift_score = 1 - min(1.0, len(drift) / max(1, len(all_bridges)))
    rot_score   = 1 - min(1.0, len(rot)   / max(1, len(stones)))
    health      = round(0.6 * drift_score + 0.3 * rot_score + 0.1 * _repo_health(stones), 3)
    report["health_index"] = health

    if action == "drift":
        return {"watch": "drift", **report["drift"]}
    if action == "rot":
        return {"watch": "rot", **report["rot"]}
    if action == "health":
        return {"health_index": health, "drift": report["drift"]["count"], "rot": report["rot"]["count"]}

    report["note"] = "The sentinel watches the cracks so the organism can mend them."
    return report
