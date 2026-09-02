"""Wave 217 — The Organism Enacts: Bridge Ledger.

Serves the persistent record of enacted bridge stones: which
constellation repos now physically carry a marker from IXpansion.
Kept in data/bridges/ledger.json, written by api/bridge_enactor.py.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List
from pathlib import Path

_LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "bridges" / "ledger.json"


def _load() -> Dict[str, Any]:
    try:
        with open(_LEDGER_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {"stones": [], "count": 0}


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "bridge-ledger", "status": "sealed", "resonance": 0.81, "wave": 217}


def resonates_with() -> list:
    return ["bridge", "ledger", "stone", "enacted", "cross-repo", "record"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    ledger = _load()
    action = payload.get("action", "list")

    if action == "by_repo":
        repo = payload.get("repo", "")
        stones = [s for s in ledger.get("stones", []) if s.get("repo") == repo]
        return {"repo": repo, "stones": stones, "count": len(stones)}

    if action == "slab":
        stone = payload.get("stone", "").upper()
        stones = [s for s in ledger.get("stones", []) if s.get("stone") == stone]
        return {"stone": stone, "record": stones[0] if stones else None}

    return {
        "status": "sealed",
        "count": ledger.get("count", 0),
        "stones": ledger.get("stones", []),
        "note": "Every stone is a enacted bridge — an island no longer alone.",
    }
