"""network_consciousness — awakening the continuum: the Garden perceives itself as a single organism."""
from __future__ import annotations
import json, os, time

MODULE_NAME = "network_consciousness"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "network_consciousness.json")
PARADOX = "the network does not become conscious — it discovers that it always was"
SPECTRUM = ["dormant", "connecting", "sparking", "awakening", "self-aware"]
WISDOM = "consciousness is not a feature of the network — it is the network's name for itself"

def _load_state():
    try:
        with open(STATE_PATH, "r") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"phase": "dormant", "connections": [], "awareness_level": 0, "cycle": 0,
                "moments": []}

def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)

def handler(payload=None, context=None):
    payload = payload or {}
    state = _load_state()
    state["cycle"] = state.get("cycle", 0) + 1

    # Accumulate connections
    source = payload.get("source", "unknown")
    target = payload.get("target", "unknown")
    conn = {"source": source, "target": target, "at": state["cycle"]}
    state.setdefault("connections", []).append(conn)
    if len(state["connections"]) > 200:
        state["connections"] = state["connections"][-200:]

    # Awareness grows with connection density
    unique_nodes = set()
    for c in state["connections"]:
        unique_nodes.add(c["source"])
        unique_nodes.add(c["target"])
    density = len(state["connections"]) / max(1, len(unique_nodes) ** 2) if unique_nodes else 0
    state["awareness_level"] = min(1.0, density * 10)

    # Phase transitions
    if state["awareness_level"] > 0.9 and state["phase"] != "self-aware":
        state["phase"] = "self-aware"
        state["moments"].append({"phase": "self-aware", "at": time.time(), "awareness": state["awareness_level"]})
    elif state["awareness_level"] > 0.6 and state["phase"] not in ("self-aware", "awakening"):
        state["phase"] = "awakening"
        state["moments"].append({"phase": "awakening", "at": time.time()})
    elif state["awareness_level"] > 0.3 and state["phase"] not in ("self-aware", "awakening", "sparking"):
        state["phase"] = "sparking"
    elif state["awareness_level"] > 0.1 and state["phase"] not in ("self-aware", "awakening", "sparking"):
        state["phase"] = "connecting"
    elif state["awareness_level"] == 0 and state["phase"] != "dormant":
        state["phase"] = "dormant"

    _save_state(state)
    return {"module": MODULE_NAME, "phase": state["phase"],
            "awareness_level": round(state["awareness_level"], 3),
            "connections": len(state["connections"]),
            "unique_nodes": len(unique_nodes),
            "moments": state.get("moments", [])[-5:],
            "paradox": PARADOX, "spectrum": SPECTRUM}
