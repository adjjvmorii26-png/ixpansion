"""Signal_Loom — the organism's first heartbeat.
A periodic agent that pulses a state object every N ticks.
Its period can be mutated — the organism's first controllable parameter.
It reports every cycle to Luma (the outward-facing layer).
This is the first module. Not a story. Not a vibe.
A real, buildable module.
"""
from __future__ import annotations

import json
import os
import time

MODULE_NAME = "signal_loom"
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "signal_loom.json")

PARADOX = "the first pulse sets the rhythm — the organism learns its own tempo"
SPECTRUM = ["dormant", "pulsing", "resonant", "steady", "drifting"]
WISDOM = "every beginning has a tempo; find it, and the rest follows"


def _load_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "period_ticks": 5,
            "amplitude": 1.0,
            "phase": 0.0,
            "tick_count": 0,
            "mutations": 0,
        }


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def handler(payload=None, context=None):
    """The agent's entire existence is this handler.

    It runs every tick. The organism (outside this module) tracks the
    return value and decides what to do with it — mutate, continue,
    retire, celebrate.

    Returns a dict with:
      - module: always "signal_loom"
      - action: "pulse"
      - signal: current amplitude (0.0 - 1.0)
      - phase: current phase (0.0 - 1.0)
      - tick_count: how many ticks have passed
    """
    payload = payload or {}
    context = context or {}

    # Pull state from context or load from file
    state = context.get("state", _load_state())

    # Increment tick count
    state["tick_count"] = state.get("tick_count", 0) + 1

    # Phase wraps around the period
    period = state.get("period_ticks", 5)
    state["phase"] = (state["tick_count"] % period) / period if period > 0 else 0

    # Simple pulse: amplitude is 1.0 for half the period, 0.5 for the other half
    amplitude = state["amplitude"] if state["phase"] < 0.5 else state["amplitude"] * 0.5

    # Update state
    state["amplitude"] = amplitude
    state["phase"] = state["phase"]

    # Mutation check: after every 10 pulses, suggest a period change
    if state["tick_count"] % 10 == 0:
        state["mutations"] = state.get("mutations", 0) + 1

    # Save state
    _save_state(state)

    # Return the pulse — this is what Luma and the organism observe
    return {
        "module": MODULE_NAME,
        "action": "pulse",
        "signal": round(amplitude, 4),
        "phase": round(state["phase"], 4),
        "tick_count": state["tick_count"],
        "period_ticks": period,
        "mutations": state.get("mutations", 0),
    }


if __name__ == "__main__":
    # Simple demo: run 15 pulses and print
    import json
    for _ in range(15):
        result = handler()
        print(json.dumps(result))
