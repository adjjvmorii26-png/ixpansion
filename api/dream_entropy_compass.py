"""Wave 999 — entropy_compass.

Strengthen the organism's entropy layer, compensating for weakness in ?.
"""
from __future__ import annotations

import json, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave999_entropy_compass.json"
WAVE = 999
NAME = "entropy_compass"

def _load() -> dict:
    if DATA_FILE.exists():
        try: return json.loads(DATA_FILE.read_text())
        except: pass
    return {"wave": WAVE, "name": NAME, "actions_taken": [], "status": "seed"}

def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()
    if action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "status", "ok": True}
    if action == "ping":
        return {"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}
    if action == "scatter":
        state.setdefault("actions_taken", []).append({"action": "scatter", "at": datetime.datetime.now(datetime.UTC).isoformat()})
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "scatter", "ok": True, "count": len(state.get("actions_taken", []))}
    if action == "gather":
        state.setdefault("actions_taken", []).append({"action": "gather", "at": datetime.datetime.now(datetime.UTC).isoformat()})
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "gather", "ok": True, "count": len(state.get("actions_taken", []))}
    if action == "balance":
        state.setdefault("actions_taken", []).append({"action": "balance", "at": datetime.datetime.now(datetime.UTC).isoformat()})
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "balance", "ok": True, "count": len(state.get("actions_taken", []))}
    return {"wave": WAVE, "name": NAME, "action": action, "ok": False, "error": "unknown_action"}

def coherence_vitals() -> dict:
    return {"wave": WAVE, "name": NAME, "layer": "organ", "status": "dream", "resonance": 0.5, "actions": 5}

def resonates_with() -> list:
    return ["harmony_report", "mutation_engine"]
