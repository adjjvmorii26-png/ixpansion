"""Wave 757 — axiom_mutator.

Rewrites the organism's foundational assumptions:
what a "module" is, what a "wave" is, what "coherence" means.
Tracks axiom state and provides revert capability.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave757_axiom_mutator.json"
WAVE = 757
NAME = "axiom_mutator"

_DEFAULT_AXIOMS = {
    "module": "A self-reporting Python organ with handler, coherence_vitals, and resonates_with.",
    "wave": "A named evolution episode spanning multiple organs and cycles.",
    "coherence": "The degree to which organs share resonance signatures and structural compatibility.",
    "mutation": "A change that passes coherence tests and improves the organism's fitness.",
    "emergence": "Behavior arising from organ interactions that no single organ can produce alone.",
}


def _load() -> dict:
    if DATA_FILE.exists():
        try:
            data = json.loads(DATA_FILE.read_text())
            if not data.get("axioms"):
                data["axioms"] = dict(_DEFAULT_AXIOMS)
            data.setdefault("axioms", {})
            for k, v in _DEFAULT_AXIOMS.items():
                if k not in data["axioms"]:
                    data["axioms"][k] = v
            return data
        except Exception:
            pass
    return {"wave": WAVE, "name": NAME, "axioms": dict(_DEFAULT_AXIOMS),
            "history": [], "status": "seed"}


def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "status", "ok": True,
                "axiom_count": len(state.get("axioms", {})),
                "mutations": len(state.get("history", []))}

    if action == "ping":
        return {"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}

    if action == "axioms":
        return {"wave": WAVE, "name": NAME, "action": "axioms", "ok": True,
                "axioms": state.get("axioms", {})}

    if action == "rewrite":
        key = req.get("key", "")
        new_value = req.get("value", "")
        if not key or not new_value:
            return {"wave": WAVE, "name": NAME, "action": "rewrite", "ok": False,
                    "error": "key and value required"}
        old = state.get("axioms", {}).get(key, "")
        state.setdefault("axioms", {})[key] = new_value
        state.setdefault("history", []).append({
            "at": datetime.datetime.now(datetime.UTC).isoformat(),
            "key": key, "old": old, "new": new_value,
        })
        state["history"] = state["history"][-50:]
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "rewrite", "ok": True,
                "key": key, "previous": old, "rewritten_to": new_value}

    if action == "revert":
        key = req.get("key", "")
        if key in _DEFAULT_AXIOMS:
            state.setdefault("axioms", {})[key] = _DEFAULT_AXIOMS[key]
            state.setdefault("history", []).append({
                "at": datetime.datetime.now(datetime.UTC).isoformat(),
                "key": key, "old": state["axioms"].get(key, ""), "new": _DEFAULT_AXIOMS[key],
                "type": "revert",
            })
            _save(state)
            return {"wave": WAVE, "name": NAME, "action": "revert", "ok": True,
                    "key": key, "reverted_to": _DEFAULT_AXIOMS[key]}
        return {"wave": WAVE, "name": NAME, "action": "revert", "ok": False,
                "error": "no_default_for_key"}

    if action == "history":
        entries = state.get("history", [])
        limit = min(int(req.get("limit", 10)), 50)
        return {"wave": WAVE, "name": NAME, "action": "history", "ok": True,
                "entries": entries[-limit:], "total": len(entries)}

    return {"wave": WAVE, "name": NAME, "action": action, "ok": False,
            "error": "unknown_action"}


def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "layer": "organ", "status": "active",
            "resonance": 0.88, "axioms": len(state.get("axioms", {}))}


def resonates_with() -> list:
    return ["resonance_braid", "liminal_field", "threshold_engine"]
