"""Wave 85 — Adaptive Regulation.

Regulation becomes contextual:
- High coherence → exploration (expansion, creativity, new connections)
- Low coherence → healing (restoration, consolidation, repair)
- Divergent coherence → mutation (structural change, evolution)

This becomes the organism's behavioral system.
"""
from __future__ import annotations
import json, time
from pathlib import Path
from typing import Any, Dict

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave85_adaptive_regulation.json"


class AdaptiveRegulator:
    """Contextual regulation system for the organism."""

    MODE_EXPLORE = "exploration"
    MODE_HEAL = "healing"
    MODE_MUTATE = "mutation"

    MODE_ACTIONS = {
        MODE_EXPLORE: ["SPAWN_NEW_MODULE", "CONNECT_DIVERSE", "EXPAND_SCOPE", "CREATE_BRIDGE"],
        MODE_HEAL: ["RESTORE_VAULT", "STABILIZE_GRADIENT", "CONSOLIDATE_MEMORY", "HEAL_WOUNDS"],
        MODE_MUTATE: ["REWRITE_RULE", "SPLIT_IDENTITY", "CREATE_PARADOX", "MUTATE_STRUCTURE"],
    }

    def __init__(self):
        self.mode = self.MODE_HEAL  # default
        self.coherence_history: list[float] = []
        self.divergence_history: list[float] = []
        self.behavior_log: list[dict] = []
        self.cycle = 0

    def classify_context(self, coherence: float, divergence: float) -> str:
        """Determine the behavioral mode from coherence and divergence."""
        if coherence >= 0.7 and divergence < 0.2:
            return self.MODE_EXPLORE
        elif coherence < 0.4:
            return self.MODE_HEAL
        elif divergence >= 0.5:
            return self.MODE_MUTATE
        elif 0.4 <= coherence < 0.7:
            return self.MODE_HEAL if len(self.coherence_history) > 0 and coherence < self.coherence_history[-1] else self.MODE_EXPLORE
        return self.MODE_HEAL

    def regulate(self, coherence: float, divergence: float = 0.0) -> dict:
        """Apply adaptive regulation based on current context."""
        self.coherence_history.append(coherence)
        self.divergence_history.append(divergence)
        if len(self.coherence_history) > 100:
            self.coherence_history.pop(0)
            self.divergence_history.pop(0)

        prev_mode = self.mode
        self.mode = self.classify_context(coherence, divergence)
        self.cycle += 1

        actions = self.MODE_ACTIONS[self.mode]
        entry = {
            "cycle": self.cycle,
            "coherence": coherence,
            "divergence": divergence,
            "mode": self.mode,
            "previous_mode": prev_mode,
            "actions": actions,
            "timestamp": time.time(),
        }
        self.behavior_log.append(entry)

        return entry

    def get_behavior_profile(self) -> dict:
        """Return the organism's behavioral profile."""
        recent = self.behavior_log[-10:] if self.behavior_log else []
        mode_counts: dict[str, int] = {}
        for entry in self.behavior_log:
            mode_counts[entry["mode"]] = mode_counts.get(entry["mode"], 0) + 1
        return {
            "current_mode": self.mode,
            "cycle": self.cycle,
            "total_cycles": len(self.behavior_log),
            "mode_distribution": mode_counts,
            "recent_actions": recent,
            "avg_coherence": sum(self.coherence_history) / len(self.coherence_history) if self.coherence_history else 0,
            "avg_divergence": sum(self.divergence_history) / len(self.divergence_history) if self.divergence_history else 0,
        }

    def get_state(self) -> dict:
        return {
            "mode": self.mode,
            "cycle": self.cycle,
            "profile": self.get_behavior_profile(),
            "action_options": self.MODE_ACTIONS[self.mode],
        }


def coherence_vitals() -> dict:
    return {"organ": "wave85_adaptive_regulation", "wave": 85, "status": "active"}

def resonates_with():
    return ['coherence_validator', 'wave84_coherence_gradient', 'wave86_coherence_memory_graph', 'wave87_coherence_integration', 'wave88_cross_realm_bridges']



def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"behavior_log": [], "coherence_history": [], "divergence_history": [], "cycle": 0}


def _save(state: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    reg = AdaptiveRegulator()
    reg.behavior_log = state.get("behavior_log", [])
    reg.coherence_history = state.get("coherence_history", [])
    reg.divergence_history = state.get("divergence_history", [])
    reg.cycle = state.get("cycle", 0)

    if action == "status":
        return {"action": "status", "wave": 85, **reg.get_state()}

    elif action == "regulate":
        coherence = req.get("coherence", 0.5)
        divergence = req.get("divergence", 0.0)
        result = reg.regulate(coherence, divergence)
        state["behavior_log"] = reg.behavior_log
        state["coherence_history"] = reg.coherence_history
        state["divergence_history"] = reg.divergence_history
        state["cycle"] = reg.cycle
        _save(state)
        return {"action": "regulate", **result}

    elif action == "profile":
        return {"action": "profile", **reg.get_behavior_profile()}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    result = handler({"action": action})
    print(json.dumps(result, indent=2, default=str))
