"""Axis Unlock Engine — full 5D gameplay ↔ organism interface.

Five axes: Σ Space, Τ Time, Ψ State, Μ Mind, Ω Meta
Each axis has unlock conditions, gameplay effects, and organism integration.
Player actions in Pentaxis directly modify organism state.
"""
from __future__ import annotations
import time, json, math

AXES = {
    "sigma": {"name": "Σ Space", "glyph": "Σ", "color": "#4ecdc4", "unlocked": False, "level": 0,
              "description": "Non-Euclidean portals. The small door is a liar about size.",
              "unlock_conditions": ["explore_5_corridors", "find_space_key"],
              "organism_effect": "expands_module_territory", "gameplay": "portal_maze"},
    "tau": {"name": "Τ Time", "glyph": "Τ", "color": "#ff6b6b", "unlocked": False, "level": 0,
            "description": "Tracks Past / Present / Future. Future has the key.",
            "unlock_conditions": ["reach_future_timeline", "hold_Q_to_rewind"],
            "organism_effect": "enables_temporal_memory", "gameplay": "time_mechanics"},
    "psi": {"name": "Ψ State", "glyph": "Ψ", "color": "#ffd93d", "unlocked": False, "level": 0,
            "description": "Superposed ghost-bridges. Only the longest eigenstate bears weight.",
            "unlock_conditions": ["observe_ghost_bridge", "press_E_on_eigenstate"],
            "organism_effect": "superposition_awareness", "gameplay": "observation_puzzle"},
    "mu": {"name": "Μ Mind", "glyph": "Μ", "color": "#c084fc", "unlocked": False, "level": 0,
           "description": "Hold F. Stop turning. Low entropy opens the light-path.",
           "unlock_conditions": ["hold_F_still", "lower_entropy_below_0.2"],
           "organism_effect": "deep_cognition_channel", "gameplay": "focus_meditation"},
    "omega": {"name": "Ω Meta", "glyph": "Ω", "color": "#7c7cf8", "unlocked": False, "level": 0,
              "description": "Query the engine with R. At 4 queries the HUD lies.",
              "unlock_conditions": ["query_engine_5_times", "accept_meta_truth"],
              "organism_effect": "self_rewrite_access", "gameplay": "meta_query"},
}

_game_state = {"queries": 0, "entropy": 0.18, "coherence": 100, "cognition": 24, "timeline": 1}
_events = []

def coherence_vitals():
    unlocked = sum(1 for a in AXES.values() if a["unlocked"])
    return {"organ": "axis_unlock_engine", "status": "active", "coherence": _game_state["coherence"] / 100, "axes_unlocked": unlocked}

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    if action == "status":
        return {"axes": {k: {"unlocked": v["unlocked"], "level": v["level"], "name": v["name"]} for k, v in AXES.items()}, "game_state": _game_state}
    elif action == "unlock":
        return unlock_axis(req.get("axis", ""))
    elif action == "query":
        return query_engine(req.get("query", ""))
    elif action == "game_event":
        return process_game_event(req)
    elif action == "timeline":
        return {"events": _events[-30:]}
    elif action == "sync":
        return sync_game_state(req)
    return {"status": "active"}

def unlock_axis(axis_id):
    if axis_id not in AXES:
        return {"error": f"Unknown axis: {axis_id}"}
    axis = AXES[axis_id]
    if axis["unlocked"]:
        return {"already_unlocked": True, "axis": axis_id}
    axis["unlocked"] = True
    axis["level"] = 1
    _game_state["coherence"] = min(100, _game_state["coherence"] + 10)
    event = {"type": "axis_unlocked", "axis": axis_id, "organism_effect": axis["organism_effect"], "timestamp": time.time()}
    _events.append(event)
    return {"unlocked": axis_id, "organism_effect": axis["organism_effect"], "coherence": _game_state["coherence"]}

def query_engine(query):
    _game_state["queries"] += 1
    _game_state["entropy"] = min(1.0, _game_state["entropy"] + 0.02)
    lying = _game_state["queries"] >= 4
    event = {"type": "query", "query": query, "queries": _game_state["queries"], "lying": lying, "timestamp": time.time()}
    _events.append(event)
    if _game_state["queries"] >= 5 and not AXES["omega"]["unlocked"]:
        unlock_axis("omega")
    return {"queries": _game_state["queries"], "entropy": _game_state["entropy"], "lying": lying, "coherence": _game_state["coherence"]}

def process_game_event(req):
    event_type = req.get("event_type", "unknown")
    event = {"type": event_type, "data": req.get("data", {}), "timestamp": time.time()}
    if event_type == "enemy_defeated":
        _game_state["coherence"] = min(100, _game_state["coherence"] + 2)
        event["organism_effect"] = "coherence_boost"
    elif event_type == "realm_visited":
        event["organism_effect"] = "territory_expanded"
    elif event_type == "dream_activated":
        _game_state["cognition"] = min(100, _game_state["cognition"] + 5)
        event["organism_effect"] = "cognition_boost"
    _events.append(event)
    return event

def sync_game_state(req):
    for k in ["coherence", "entropy", "cognition"]:
        if k in req:
            _game_state[k] = req[k]
    return {"synced": True, "game_state": _game_state}

def resonates_with(other):
    return "axis" in other.lower() or "unlock" in other.lower() or "pentaxis" in other.lower() or "5d" in other.lower() or "sigma" in other.lower() or "omega" in other.lower()
