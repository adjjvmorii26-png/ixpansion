"""Wave 636 — Adaptive Regulation.

Regulation becomes contextual:
- High coherence → exploration mode (let modules roam)
- Low coherence → healing mode (conserve energy)
- Divergent coherence → mutation mode (change structure)
This becomes the organism's behavioral system.
"""
import json, time
from pathlib import Path

STATE = Path("data/wave636_adaptive_regulation.json")

def _load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {
        "mode_history": [],
        "current_mode": "healing",
        "policies": {},
        "regulation_cycles": 0,
        "tick": 0,
    }

def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2))

def _now():
    return time.time()

MODES = {
    "exploration": {
        "desc": "High coherence — modules roam freely, new connections encouraged",
        "energy_level": "high",
        "mutation_allowed": False,
        "new_connections": True,
        "threshold": 0.75,
    },
    "healing": {
        "desc": "Low coherence — conserve energy, stabilize existing structure",
        "energy_level": "conserving",
        "mutation_allowed": False,
        "new_connections": False,
        "threshold": 0.4,
    },
    "mutation": {
        "desc": "Divergent coherence — change structure to break deadlock",
        "energy_level": "chaotic",
        "mutation_allowed": True,
        "new_connections": True,
        "threshold": 0.6,
    },
}

def _evaluate(avg_coherence, variance):
    """Determine the organism's regulatory mode based on coherence signals."""
    if avg_coherence >= MODES["exploration"]["threshold"] and variance < 0.1:
        return "exploration"
    if avg_coherence < MODES["healing"]["threshold"]:
        return "healing"
    if variance > 0.25:
        return "mutation"
    return "healing"

def _set_policy(mode, key, value):
    s = _load()
    s["policies"].setdefault(mode, {})[key] = value
    _save(s)
    return {"ok": True, "mode": mode, "policy_key": key, "value": value}

def _assess(coherence_data):
    """Run a full regulatory cycle on coherence data."""
    s = _load()
    s["regulation_cycles"] += 1
    s["tick"] += 1

    modules = coherence_data.get("modules", {})
    if not modules:
        avg_coherence = coherence_data.get("avg_coherence", 0.5)
        variance = coherence_data.get("variance", 0.0)
    else:
        values = list(modules.values())
        avg_coherence = sum(values) / len(values)
        variance = sum((v - avg_coherence) ** 2 for v in values) / len(values)

    new_mode = _evaluate(avg_coherence, variance)
    old_mode = s["current_mode"]

    s["current_mode"] = new_mode
    s["mode_history"].append({
        "cycle": s["regulation_cycles"],
        "from": old_mode,
        "to": new_mode,
        "avg_coherence": round(avg_coherence, 4),
        "variance": round(variance, 4),
        "time": _now(),
    })
    s["mode_history"] = s["mode_history"][-100:]
    _save(s)

    return {
        "cycle": s["regulation_cycles"],
        "mode": new_mode,
        "mode_info": MODES[new_mode],
        "avg_coherence": round(avg_coherence, 4),
        "variance": round(variance, 4),
        "mode_changed": old_mode != new_mode,
    }

def _mode_matrix():
    """Show all modes and their transition logic."""
    return {"modes": MODES, "current": _load()["current_mode"]}

def _status():
    s = _load()
    return {
        "tick": s["tick"],
        "current_mode": s["current_mode"],
        "cycles": s["regulation_cycles"],
        "policies": s["policies"],
        "recent_transitions": s["mode_history"][-3:],
    }

def _policy_check(mode, proposed_action):
    """Check if an action aligns with the current regulatory mode."""
    s = _load()
    mode_policies = s["policies"].get(mode, {})
    allowed = True
    reason = None

    if proposed_action == "create_module":
        if not MODES[mode]["new_connections"]:
            allowed = False
            reason = "Healing mode conserves structure — no new modules"
    elif proposed_action == "mutate_module":
        if not MODES[mode]["mutation_allowed"]:
            allowed = False
            reason = f"{mode.capitalize()} mode does not permit mutation"
    elif proposed_action == "remove_module":
        if mode == "mutation":
            allowed = False
            reason = "Mutation mode protects structure from removal"

    return {"allowed": allowed, "reason": reason, "mode": mode}

def handler(req):
    action = req.get("action", "status")
    if action == "status":
        return {"ok": True, **_status()}
    elif action == "assess":
        return {"ok": True, **_assess(req.get("coherence", {}))}
    elif action == "set_policy":
        return {"ok": True, **_set_policy(req.get("mode", "healing"), req.get("key", ""), req.get("value", True))}
    elif action == "modes":
        return {"ok": True, **_mode_matrix()}
    elif action == "policy_check":
        r = _policy_check(req.get("mode", _load()["current_mode"]), req.get("action_name", ""))
        return {"ok": True, **r}
    return {"ok": False, "error": f"Unknown action: {action}"}

def coherence_vitals():
    s = _load()
    return {"wave": 636, "mode": s["current_mode"], "cycles": s["regulation_cycles"]}

def resonates_with():
    return ["wave635_coherence_gradient", "wave634_temporal_field", "wave622_resilience_mesh"]
