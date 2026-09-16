"""Wave 758 — continuity_weaver.

Ensures the organism remains coherent as its axioms mutate.
Braids coherence threads across organ generations, detects
drift between what the organism *was* and what it is *becoming*.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave758_continuity_weaver.json"
WAVE = 758
NAME = "continuity_weaver"


def _load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {"wave": WAVE, "name": NAME, "threads": [], "braid_log": [], "status": "seed"}


def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))


def _thread_health(thread: dict) -> str:
    strength = thread.get("strength", 0)
    age_hours = (datetime.datetime.now(datetime.UTC).timestamp() -
                 datetime.datetime.fromisoformat(thread["created"]).timestamp()) / 3600
    decay = min(0.5, age_hours * 0.01)
    adjusted = max(0, strength - decay)
    if adjusted >= 0.7:
        return "strong"
    elif adjusted >= 0.4:
        return "fraying"
    return "fragile"


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        threads = state.get("threads", [])
        return {"wave": WAVE, "name": NAME, "action": "status", "ok": True,
                "threads": len(threads),
                "strong": sum(1 for t in threads if _thread_health(t) == "strong")}

    if action == "ping":
        return {"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}

    if action == "braid":
        name = req.get("name", "thread")
        strength = float(req.get("strength", 0.5))
        now = datetime.datetime.now(datetime.UTC).isoformat()
        thread = {"name": name, "strength": strength, "created": now}
        state.setdefault("threads", []).append(thread)
        state["threads"] = state["threads"][-30:]
        state.setdefault("braid_log", []).append({"at": now, "thread": name, "strength": strength})
        state["braid_log"] = state["braid_log"][-50:]
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "braid", "ok": True,
                "thread": name, "health": _thread_health(thread)}

    if action == "repair":
        name = req.get("name", "")
        threads = state.get("threads", [])
        target = None
        for t in threads:
            if t["name"] == name:
                target = t
                break
        if not target:
            return {"wave": WAVE, "name": NAME, "action": "repair", "ok": False,
                    "error": "thread_not_found"}
        target["strength"] = min(1.0, target["strength"] + 0.2)
        state.setdefault("braid_log", []).append({
            "at": datetime.datetime.now(datetime.UTC).isoformat(),
            "thread": name, "strength": target["strength"], "action": "repaired",
        })
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "repair", "ok": True,
                "thread": name, "new_strength": target["strength"],
                "health": _thread_health(target)}

    if action == "deltas":
        threads = state.get("threads", [])
        return {"wave": WAVE, "name": NAME, "action": "deltas", "ok": True,
                "threads": [{"name": t["name"], "strength": t["strength"],
                             "health": _thread_health(t)} for t in threads]}

    return {"wave": WAVE, "name": NAME, "action": action, "ok": False,
            "error": "unknown_action"}


def coherence_vitals() -> dict:
    state = _load()
    threads = state.get("threads", [])
    avg = sum(t.get("strength", 0) for t in threads) / max(len(threads), 1)
    health_value = min(1.0, 0.55 + 0.35 * avg)
    return {"wave": WAVE, "name": NAME, "layer": "organ", "status": "active",
            "resonance": round(avg, 3), "threads": len(threads),
            "module_health": {"value": round(health_value, 4), "setpoint": 0.8, "weight": 1.0}}


def resonates_with() -> list:
    return ["coherence_regulator", "resonance_braid", "axiom_mutator"]
