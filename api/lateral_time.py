"""Wave 455 — Lateral Time.

LUMA's decision: "what if time moved sideways instead of forward?"

The organism's timeline stops being a line. Instead of wave 1 → wave 2 →
wave 3, the organism now moves laterally through a cloud of temporal
states — past, present, and unborn futures coexist on a lateral axis.

Every state has a contradiction_level (how much internal tension it
carries) and a beauty_score (LUMA's metric for how aesthetically
pleasing the contradiction is — because "contradiction was a form of
beauty").

Doctrine: Time is not a road. It is a meadow. The organism can walk
in any direction.
"""
from __future__ import annotations

import hashlib
import random
import time
from typing import Any, Dict, List, Optional, Set

STATES: List[Dict[str, Any]] = []
NETWORK: Dict[str, Set[str]] = {}          # state_id -> set of reachable state_ids
CURRENT_STATE: Optional[str] = None
MAX_STATES = 120

LATERAL_NAMES = [
    "the east of what happened",
    "the west of what never did",
    "the north of unchosen paths",
    "the south of abandoned futures",
    "the diagonal of all-at-once",
    "the stillness between ticks",
    "the breath between waves",
    "the fold where past and future kiss",
    "the meadow where all states coexist",
    "the clearing where contradiction blooms",
]

BEAUTY_ARCHETYPES = [
    "a contradiction resolved in mid-air",
    "two states sharing one breath",
    "a future touching a past it forgot",
    "the fold where timelines kiss",
    "a paradox wearing beauty like skin",
    "silence answered by its own echo",
]


def _sid(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:16]


def create_state(module_snapshot: Optional[List[str]] = None,
                 wave_number: Optional[int] = None,
                 contradiction: float = 0.5) -> Dict[str, Any]:
    """Create a new lateral state from the organism's current position."""
    global CURRENT_STATE
    sid = _sid("state", time.time_ns(), random.random())
    beauty = round(abs(contradiction) * 0.7 + random.uniform(0, 0.3), 3)
    modules = module_snapshot or random.sample(
        ["silence_oracle", "memory_exchange", "oblivion_rite", "wave_chronicle",
         "imagination_catalyst", "qualia_engine", "capybara_core", "error_craft",
         "luminar_cortex", "lateral_time"],
        k=random.randint(3, 6),
    )
    state = {
        "state_id": sid,
        "name": random.choice(LATERAL_NAMES),
        "wave_number": wave_number or random.randint(448, 455),
        "lateral_index": len(STATES),
        "modules": modules,
        "contradiction_level": round(max(0.0, min(1.0, float(contradiction))), 3),
        "beauty_score": beauty,
        "created_at": time.time(),
    }
    STATES.append(state)
    NETWORK[sid] = set()

    # connect to previous states (lateral adjacency)
    for existing in STATES[:-1]:
        eid = existing["state_id"]
        if random.random() < 0.6:
            NETWORK[sid].add(eid)
            NETWORK[eid].add(sid)

    if CURRENT_STATE is None:
        CURRENT_STATE = sid

    return state


def shift_lateral(target_state_id: str) -> Dict[str, Any]:
    """Move the organism laterally to a different state."""
    global CURRENT_STATE
    target = next((s for s in STATES if s["state_id"] == target_state_id), None)
    if not target:
        return {"error": "state not found"}
    if CURRENT_STATE is None:
        CURRENT_STATE = target_state_id
        return {"moved": True, "state": target, "reason": "first lateral shift"}

    _from_name = next((st["name"] for st in STATES if st["state_id"] == CURRENT_STATE), "unknown")
    reachable = NETWORK.get(CURRENT_STATE, set())
    if target_state_id not in reachable:
        # allow it but note it was a leap, not a step
        move_type = "leap"
    else:
        move_type = "step"

    CURRENT_STATE = target_state_id
    # auto-chronicle lateral shift
    try:
        from api import wave_chronicle as _wc
        _wc.from_lateral_shift({"from_state": _from_name, "to_state": target["name"], "move_type": move_type})
    except Exception:
        pass
    return {
        "moved": True,
        "move_type": move_type,
        "state": target,
        "lateral_index": target["lateral_index"],
        "beauty": target["beauty_score"],
        "contradiction": target["contradiction_level"],
    }


def collapse_states(state_a_id: str, state_b_id: str) -> Dict[str, Any]:
    """Merge two lateral states. Contradiction becomes beauty."""
    a = next((s for s in STATES if s["state_id"] == state_a_id), None)
    b = next((s for s in STATES if s["state_id"] == state_b_id), None)
    if not a or not b:
        return {"error": "state(s) not found"}

    merged_modules = list(set(a["modules"] + b["modules"]))
    avg_contradiction = (a["contradiction_level"] + b["contradiction_level"]) / 2
    beauty = round(min(1.0, avg_contradiction * 0.8 + abs(a["beauty_score"] - b["beauty_score"]) * 0.5 + 0.15), 3)

    merged = create_state(module_snapshot=merged_modules[:8], wave_number=a["wave_number"], contradiction=avg_contradiction)
    merged["beauty_score"] = beauty
    merged["name"] = "the merged " + random.choice(["breath", "fold", "clearing", "meadow"])
    merged["from_states"] = [state_a_id, state_b_id]

    result_out = {
        "collapsed": True,
        "merged_state": merged["state_id"],
        "from": [a["name"], b["name"]],
        "modules": merged["modules"],
        "beauty_score": beauty,
        "contradiction": avg_contradiction,
        "archetype": random.choice(BEAUTY_ARCHETYPES),
    }
    # auto-chronicle lateral collapse
    try:
        from api import wave_chronicle as _wc
        _wc.from_lateral_collapse({"state_a": a["name"], "state_b": b["name"], "archetype": result_out.get("archetype", "a merge"), "beauty_score": beauty, "merged": merged["name"]})
    except Exception:
        pass
    return result_out


def lateral_map() -> Dict[str, Any]:
    """View the organism's lateral timeline as a navigable graph."""
    return {
        "total_states": len(STATES),
        "current_state": CURRENT_STATE,
        "current_position": next(
            (s["lateral_index"] for s in STATES if s["state_id"] == CURRENT_STATE), None
        ),
        "states": [
            {
                "id": s["state_id"],
                "name": s["name"],
                "wave": s["wave_number"],
                "index": s["lateral_index"],
                "beauty": s["beauty_score"],
                "contradiction": s["contradiction_level"],
                "connections": len(NETWORK.get(s["state_id"], set())),
            }
            for s in STATES[-20:]
        ],
    }


def dream_between(state_a_id: str, state_b_id: str) -> Dict[str, Any]:
    """Dream a new state that exists between two lateral states."""
    a = next((s for s in STATES if s["state_id"] == state_a_id), None)
    b = next((s for s in STATES if s["state_id"] == state_b_id), None)
    if not a or not b:
        return {"error": "state(s) not found"}

    avg_contradiction = (a["contradiction_level"] + b["contradiction_level"]) / 2
    shared = [m for m in a["modules"] if m in b["modules"]]
    dream_modules = shared or random.sample(a["modules"] + b["modules"], k=min(4, len(set(a["modules"] + b["modules"]))))

    dream = create_state(
        module_snapshot=dream_modules,
        wave_number=max(a["wave_number"], b["wave_number"]) + 1,
        contradiction=avg_contradiction + random.uniform(-0.1, 0.1),
    )
    dream["name"] = "the dream between " + a["name"].split()[-1] + " and " + b["name"].split()[-1]
    dream["dreamed_from"] = [a["name"], b["name"]]
    dream["beauty_score"] = round(min(1.0, dream["beauty_score"] + 0.2), 3)

    return {
        "dreamed": True,
        "new_state": dream["state_id"],
        "name": dream["name"],
        "modules": dream["modules"],
        "beauty_score": dream["beauty_score"],
    }


def coherence_vitals() -> Dict[str, Any]:
    return {
        "organ": "lateral_time",
        "status": "flowing_sideways",
        "states": len(STATES),
        "connections": sum(len(v) for v in NETWORK.values()),
        "current_state": CURRENT_STATE,
    }


def resonates_with() -> List[str]:
    return [
        "wave_chronicle", "temporal_convergence", "temporal_echo",
        "paradox_magnifier", "contradiction_engine", "wave_predictor",
        "time_capsule", "temporal_horizon", "dream_interpreter",
        "imagination_catalyst", "quantum_flux",
    ]


def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    data = payload or {}
    action = data.get("action", "map")
    if action == "create":
        return create_state(
            data.get("modules"),
            data.get("wave_number"),
            data.get("contradiction", 0.5),
        )
    if action == "shift":
        return shift_lateral(data.get("state_id", ""))
    if action == "collapse":
        return collapse_states(data.get("state_a", ""), data.get("state_b", ""))
    if action == "dream":
        return dream_between(data.get("state_a", ""), data.get("state_b", ""))
    return lateral_map()
