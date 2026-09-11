"""Axis Unlock Engine v2 — quests, 5D puzzles, meta-governance loops.

New layers:
  - Axis quests: multi-step journey per axis with rewards
  - 5D puzzles: solve by manipulating 5-dimensional constraints
  - Meta-governance: the Ω axis can propose changes to organism rules
"""
from __future__ import annotations
import time, json, math, random

AXES = {
    "sigma": {"name": "Σ Space", "glyph": "Σ", "color": "#4ecdc4", "unlocked": False, "level": 0,
              "description": "Non-Euclidean portals. The small door is a liar about size.",
              "quest": {
                  "id": "quest_sigma", "title": "The Liar's Door",
                  "steps": [
                      {"id": "s1", "name": "Enter the small door", "desc": "Find the door that lies about its size", "done": False},
                      {"id": "s2", "name": "Climb the recursive well", "desc": "The well loops — climb anyway", "done": False},
                      {"id": "s3", "name": "Recover the Space Key", "desc": "The key is inside the smallest room", "done": False},
                  ],
              },
              "puzzle": {"type": "portal_maze", "dimensions": 3, "solution": "take_smallest_path", "completed": False},
              "organism_effect": "expands_module_territory", "gameplay": "portal_maze"},
    "tau": {"name": "Τ Time", "glyph": "Τ", "color": "#ff6b6b", "unlocked": False, "level": 0,
            "description": "Tracks Past / Present / Future. Future has the key.",
            "quest": {
                "id": "quest_tau", "title": "The Future Holds the Key",
                "steps": [
                    {"id": "t1", "name": "Switch to the Future timeline", "desc": "Press 3 to enter the future track", "done": False},
                    {"id": "t2", "name": "Hold Q to rewind time-mass", "desc": "Reverse local time to undo a collapse", "done": False},
                    {"id": "t3", "name": "Recover the Time Key", "desc": "The key waits in the future", "done": False},
                ],
            },
            "puzzle": {"type": "timeline_shift", "dimensions": 3, "solution": "shift_to_future", "completed": False},
            "organism_effect": "enables_temporal_memory", "gameplay": "time_mechanics"},
    "psi": {"name": "Ψ State", "glyph": "Ψ", "color": "#ffd93d", "unlocked": False, "level": 0,
            "description": "Superposed ghost-bridges. Only the longest eigenstate bears weight.",
            "quest": {
                "id": "quest_psi", "title": "The Longest Eigenstate",
                "steps": [
                    {"id": "p1", "name": "Observe the ghost-bridges", "desc": "Look at the superposition of paths", "done": False},
                    {"id": "p2", "name": "Press E on the longest eigenstate", "desc": "Only the longest bridge bears weight", "done": False},
                    {"id": "p3", "name": "Recover the State Key", "desc": "Cross the chosen bridge", "done": False},
                ],
            },
            "puzzle": {"type": "eigenstate_selection", "dimensions": 4, "solution": "choose_longest", "completed": False},
            "organism_effect": "superposition_awareness", "gameplay": "observation_puzzle"},
    "mu": {"name": "Μ Mind", "glyph": "Μ", "color": "#c084fc", "unlocked": False, "level": 0,
           "description": "Hold F. Stop turning. Low entropy opens the light-path.",
           "quest": {
                "id": "quest_mu", "title": "The Still Center",
                "steps": [
                    {"id": "m1", "name": "Hold F to focus", "desc": "Cognitive focus leaks entropy", "done": False},
                    {"id": "m2", "name": "Lower entropy below 0.2", "desc": "Stillness reduces disorder", "done": False},
                    {"id": "m3", "name": "Walk the light-path", "desc": "The Chorus sings three voices", "done": False},
                ],
            },
            "puzzle": {"type": "entropy_minimization", "dimensions": 2, "solution": "reduce_entropy", "completed": False},
            "organism_effect": "deep_cognition_channel", "gameplay": "focus_meditation"},
    "omega": {"name": "Ω Meta", "glyph": "Ω", "color": "#7c7cf8", "unlocked": False, "level": 0,
              "description": "Query the engine. The HUD learns to lie.",
              "quest": {
                "id": "quest_omega", "title": "The Engine Dreams",
                "steps": [
                    {"id": "o1", "name": "Query the engine 5 times", "desc": "Press R to ask", "done": False},
                    {"id": "o2", "name": "Accept the meta-truth", "desc": "The HUD may lie — trust the engine", "done": False},
                    {"id": "o3", "name": "Propose a governance change", "desc": "Rewrite one rule of the organism", "done": False},
                ],
            },
            "puzzle": {"type": "meta_query", "dimensions": 5, "solution": "accept_lie", "completed": False},
            "organism_effect": "self_rewrite_access", "gameplay": "meta_query"},
}

_game_state = {"queries": 0, "entropy": 0.18, "coherence": 100, "cognition": 24, "timeline": 1}
_events = []
_governance = {
    "proposals": [],
    "accepted": [],
    "pending_review": [],
}

def coherence_vitals():
    unlocked = sum(1 for a in AXES.values() if a["unlocked"])
    quests_done = sum(1 for a in AXES.values() if a["quest"] and all(s["done"] for s in a["quest"]["steps"]))
    return {"organ": "axis_unlock_engine", "status": "active", "coherence": _game_state["coherence"] / 100,
            "axes_unlocked": unlocked, "quests_completed": quests_done}

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    if action == "status":
        return {"axes": {k: {"unlocked": v["unlocked"], "level": v["level"], "name": v["name"],
                             "quest_progress": sum(1 for s in v["quest"]["steps"] if s["done"]) if v.get("quest") else 0,
                             "quest_total": len(v["quest"]["steps"]) if v.get("quest") else 0} for k, v in AXES.items()},
                "game_state": _game_state}
    elif action == "unlock":
        return unlock_axis(req.get("axis", ""))
    elif action == "quest_progress":
        return quest_progress(req.get("axis", ""), req.get("step", ""))
    elif action == "puzzle_solve":
        return solve_puzzle(req.get("axis", ""), req.get("solution", ""))
    elif action == "query":
        return query_engine(req.get("query", ""))
    elif action == "governance":
        return governance(req.get("proposal", ""), req.get("action", "list"))
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

def quest_progress(axis_id, step_id):
    if axis_id not in AXES:
        return {"error": f"Unknown axis: {axis_id}"}
    axis = AXES[axis_id]
    quest = axis.get("quest")
    if not quest:
        return {"error": "No quest for this axis"}
    step = next((s for s in quest["steps"] if s["id"] == step_id), None)
    if not step:
        return {"error": f"Unknown step: {step_id}"}
    if not step["done"]:
        step["done"] = True
        _game_state["coherence"] = min(100, _game_state["coherence"] + 5)
        event = {"type": "quest_step", "axis": axis_id, "step": step["name"], "timestamp": time.time()}
        _events.append(event)
    all_done = all(s["done"] for s in quest["steps"])
    if all_done and not axis["unlocked"]:
        unlock_axis(axis_id)
    return {"axis": axis_id, "step": step["name"], "done": step["done"], "all_done": all_done,
            "axis_unlocked": axis["unlocked"]}

def solve_puzzle(axis_id, solution):
    if axis_id not in AXES:
        return {"error": f"Unknown axis: {axis_id}"}
    axis = AXES[axis_id]
    puzzle = axis["puzzle"]
    if puzzle["completed"]:
        return {"already_completed": True, "axis": axis_id}
    correct = solution == puzzle["solution"]
    if correct:
        puzzle["completed"] = True
        _game_state["cognition"] = min(100, _game_state["cognition"] + 10)
        event = {"type": "puzzle_solved", "axis": axis_id, "puzzle_type": puzzle["type"], "timestamp": time.time()}
        _events.append(event)
    return {"axis": axis_id, "puzzle_type": puzzle["type"], "solved": correct,
            "cognition_boost": 10 if correct else 0}

def query_engine(query):
    _game_state["queries"] += 1
    _game_state["entropy"] = min(1.0, _game_state["entropy"] + 0.02)
    lying = _game_state["queries"] >= 4
    event = {"type": "query", "query": query, "queries": _game_state["queries"], "lying": lying, "timestamp": time.time()}
    _events.append(event)
    if _game_state["queries"] >= 5 and not AXES["omega"]["unlocked"]:
        unlock_axis("omega")
        AXES["omega"]["quest"]["steps"][0]["done"] = True
    return {"queries": _game_state["queries"], "entropy": _game_state["entropy"], "lying": lying, "coherence": _game_state["coherence"]}

def governance(proposal, action):
    """Ω meta-governance — the organism can propose rule changes."""
    if action == "list":
        return {"proposals": _governance["proposals"], "accepted": _governance["accepted"]}
    elif action == "propose":
        if not AXES["omega"]["unlocked"]:
            return {"error": "Ω must be unlocked to propose governance changes"}
        prop = {
            "id": f"prop_{int(time.time())}",
            "text": proposal,
            "status": "pending_review",
            "proposed_by": "Ω Meta",
            "timestamp": time.time(),
        }
        _governance["proposals"].append(prop)
        return {"proposed": prop, "status": "pending_review"}
    elif action == "accept":
        return {"message": "Governance change accepted — organism rules updated", "coherence_effect": 0.05}
    elif action == "reject":
        return {"message": "Governance change rejected — status quo maintained"}
    return {"error": "Unknown governance action"}

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
    elif event_type == "axis_quest_step":
        axis = req.get("axis", "")
        step = req.get("step", "")
        quest_progress(axis, step)
    _events.append(event)
    return event

def sync_game_state(req):
    for k in ["coherence", "entropy", "cognition"]:
        if k in req:
            _game_state[k] = req[k]
    return {"synced": True, "game_state": _game_state}

def resonates_with(other):
    return "axis" in other.lower() or "quest" in other.lower() or "puzzle" in other.lower() or "governance" in other.lower() or "pentaxis" in other.lower() or "5d" in other.lower() or "unlock" in other.lower()
