"""Wave 728 — Veil Lifter.

Reveals hidden relationships between modules
that were previously invisible to the architecture.
"""
import json, hashlib
from pathlib import Path
from typing import Any, Dict
import datetime

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave728_veil_lifter.json"
WAVE = 728
NAME = "veil_lifter"

def _load() -> dict:
    return json.loads(DATA_FILE.read_text()) if DATA_FILE.exists() else {"wave": WAVE, "name": NAME, "revealed": [], "hidden": []}

def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()
    if action == "lift":
        mod_a, mod_b = req.get("module_a", ""), req.get("module_b", "")
        hash_key = hashlib.md5(f"{mod_a}:{mod_b}".encode()).hexdigest()[:8]
        reveal = {"id": hash_key, "modules": [mod_a, mod_b], "relationship": "hidden_symmetry", "wave": WAVE, "revealed_at": datetime.datetime.now(datetime.UTC).isoformat()}
        state["revealed"].append(reveal)
        _save(state)
        return {"wave": WAVE, "action": "lift", "reveal": reveal}
    elif action == "hidden":
        return {"wave": WAVE, "hidden": state["hidden"][-20:], "revealed_count": len(state["revealed"])}
    elif action == "status":
        return {"wave": WAVE, "revealed": len(state["revealed"]), "status": "active"}
    return {"wave": WAVE, "action": action, "status": "ok"}

def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "revealed": len(state["revealed"]), "status": "active"}

def resonates_with() -> list:
    return [720, 726, 727]
