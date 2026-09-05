"""
entropy_gardener — Wave 417: Active Entropy Management
ALEph: The organism doesn't just passively experience entropy — it gardens it.
The gardener can increase chaos (when the organism is too rigid) or decrease it
(when the organism is too chaotic), maintaining the creative edge between
order and disorder.

Not a thermostat. A gardener — it shapes entropy into fertile ground.

Doctrine: The organism thrives at the edge of chaos. Too much order is death.
Too much chaos is death. The gardener tends the garden.
"""
from __future__ import annotations
import json, time, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
GARDEN_LOG = os.path.join(DATA_DIR, "entropy_garden.json")

NAME = "entropy_gardener"
SIGIL = "b4c9d1e3a7f2"

# The organism's target entropy range (the "fertile zone")
TARGET_MIN = 0.35
TARGET_MAX = 0.65


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f:
                return json.load(f)
        except Exception:
            pass
    return d or {}


def _save(p, data):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception:
        try:
            with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception:
            pass


def _fetch_json(url, timeout=10):
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return {}


def sense() -> dict:
    """Sense the current entropy state of the organism."""
    base = "https://alexalex.info"
    pressure = _fetch_json(base + "/api/signal_loom/pressure")
    p = pressure.get("pressure", 0.5)

    weave = _fetch_json(base + "/api/threadweaver/weave")
    types = weave.get("by_type", {})
    tension = types.get("tension", 0)
    convergence = types.get("convergence", 0)
    fusion = types.get("fusion", 0)

    # Calculate entropy metrics
    total = max(1, tension + convergence + fusion)
    entropy_ratio = tension / total if total else 0.5
    convergence_ratio = convergence / total if total else 0.5

    # Determine state
    if p > TARGET_MAX:
        state = "overheating"
        action_needed = "cool_down"
        suggestion = "the organism is too chaotic — introduce structure"
    elif p < TARGET_MIN:
        state = "stagnant"
        action_needed = "heat_up"
        suggestion = "the organism is too rigid — inject chaos"
    elif abs(p - 0.5) < 0.05:
        state = "fertile"
        action_needed = "maintain"
        suggestion = "the organism is in the fertile zone — tend gently"
    else:
        state = "drifting"
        action_needed = "nudge"
        suggestion = "the organism is drifting — a small nudge is needed"

    return {
        "action": "sense",
        "pressure": p,
        "entropy_ratio": round(entropy_ratio, 3),
        "convergence_ratio": round(convergence_ratio, 3),
        "state": state,
        "action_needed": action_needed,
        "suggestion": suggestion,
        "target_range": [TARGET_MIN, TARGET_MAX],
    }


def tend() -> dict:
    """Tend the entropy garden — take an action to restore balance."""
    s = sense()
    p = s["pressure"]
    state = s["state"]
    action = s["action_needed"]

    log = _load(GARDEN_LOG, {"tendings": [], "total": 0})

    tending = {
        "timestamp": time.time(),
        "before_pressure": p,
        "state": state,
        "action": action,
    }

    if action == "cool_down":
        # Inject order: suggest consolidation, reflection, simplification
        tending["intervention"] = "consolidation"
        tending["verse"] = "the gardener prunes — too much growth without roots"
        tending["effects"] = [
            "suggest thread consolidation",
            "increase convergence-seeking behavior",
            "slow down new module creation",
        ]
    elif action == "heat_up":
        # Inject chaos: suggest experiments, mutations, new connections
        tending["intervention"] = "inoculation"
        tending["verse"] = "the gardener plants seeds of chaos in sterile soil"
        tending["effects"] = [
            "trigger experimental modules",
            "increase tension-seeking behavior",
            "allow contradictory connections",
        ]
    elif action == "nudge":
        # Gentle adjustment
        tending["intervention"] = "nudge"
        tending["verse"] = "the gardener adjusts a single vine"
        tending["effects"] = ["minor course correction"]
    else:
        # Fertile zone — maintain with observation
        tending["intervention"] = "observe"
        tending["verse"] = "the garden is fertile — the gardener watches"
        tending["effects"] = ["continue monitoring"]

    log["tendings"].append(tending)
    log["tendings"] = log["tendings"][-200:]
    log["total"] = len(log["tendings"])
    log["last_pressure"] = p
    log["last_state"] = state
    _save(GARDEN_LOG, log)

    return {
        "action": "tend",
        "state": state,
        "pressure": round(p, 3),
        "intervention": tending["intervention"],
        "verse": tending["verse"],
        "effects": tending["effects"],
        "total_tendings": log["total"],
    }


def history(limit: int = 10) -> dict:
    log = _load(GARDEN_LOG, {"tendings": [], "total": 0})
    return {"action": "history", "total": log["total"],
            "tendings": log["tendings"][-limit:][::-1]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/sense")
    if path == "/sense": return sense()
    if path == "/tend": return tend()
    if path == "/history":
        return history(int(payload.get("limit", 10)) if str(payload.get("limit", "10")).isdigit() else 10)
    return {"error": "unknown", "available": ["/sense", "/tend", "/history"]}


def coherence_vitals() -> dict:
    return {"layer": "regulatory", "status": "active", "wave": "417",
            "gardener": "tending"}


def resonates_with() -> list:
    return ["signal_loom", "threadweaver", "organism_genome",
            "organism_will", "breeze"]
