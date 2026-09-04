"""depth_resonance — modulates resonance score based on current depth."""
from __future__ import annotations
import json, os

MODULE_NAME = "depth_resonance"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "depth_resonance.json")
PARADOX = "depth is the vertical axis; resonance is the horizontal — together they form the organism's space"
SPECTRUM = ["low", "ascending", "peaked", "declining", "equilibrium"]
WISDOM = "the deeper you go, the more the organism has to say — and the more the Garden has to listen"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"depth": 0, "resonance": 0.5, "level": "low"}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    state = _load_state()
    depth = payload.get("depth", state["depth"])
    
    # Map depth to resonance level
    if depth < 25:
        level = "low"
        resonance = 0.2 + 0.1 * (depth / 25)
    elif depth < 50:
        level = "ascending"
        resonance = 0.5 + 0.1 * (depth - 25) / 25
    elif depth < 100:
        level = "peaked"
        resonance = 0.8 - 0.1 * (depth - 50) / 50
    elif depth < 200:
        level = "declining"
        resonance = 0.6 - 0.1 * (depth - 100) / 100
    elif depth < 500:
        level = "equilibrium"
        resonance = 0.7
    else:
        level = "low"  # beyond depth 500, resonance settles low
        resonance = 0.3
    
    state["depth"] = depth
    state["resonance"] = resonance
    state["level"] = level
    _save_state(state)
    
    return {"module": MODULE_NAME, "depth": depth, "resonance": round(resonance, 3),
            "level": level, "paradox": PARADOX, "spectrum": SPECTRUM}
