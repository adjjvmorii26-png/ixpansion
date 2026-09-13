"""Wave 87 — Coherence Integration.

Synthesizes waves 84-86 into a unified organism-wide coherence system.
This wave becomes the organism's "consciousness director" — it doesn't
just measure coherence, it actively directs it toward stable patterns.

Integration triad:
- Gradient field (wave 84): spatial coherence distribution
- Adaptive regulation (wave 85): behavioral mode selection  
- Memory graph (wave 86): temporal coherence persistence

The organism doesn't react randomly — it has a directed coherence policy.
"""
from __future__ import annotations
import json, time, math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave87_coherence_integration.json"


class CoherencePolicy:
    """Directed coherence policy for the organism."""

    # Policy weights for different coherence sources
    GRADIENT_WEIGHT = 0.4    # from wave 84 gradient field
    REGULATION_WEIGHT = 0.3  # from wave 85 adaptive regulation
    MEMORY_WEIGHT = 0.3      # from wave 86 coherence memory

    def __init__(self):
        self.target_coherence = 0.65
        self.stability_threshold = 0.55
        self.divergence_limit = 0.45

    def evaluate(self, gradient_data: dict, regulation_data: dict, memory_data: dict) -> dict:
        """Evaluate overall coherence from all three subsystems."""
        # Extract key metrics
        grad_avg = gradient_data.get("average_coherence", 0.5)
        reg_mode = regulation_data.get("current_mode", "healing")
        mem_recent = memory_data.get("recent_coherence", 0.5)

        # Weight the contributions
        policy_score = (
            self.GRADIENT_WEIGHT * grad_avg +
            self.REGULATION_WEIGHT * self._mode_score(reg_mode) +
            self.MEMORY_WEIGHT * mem_recent
        )

        # Determine policy action
        action = self._determine_action(policy_score, reg_mode, mem_recent)

        return {
            "policy_score": round(policy_score, 4),
            "target_coherence": self.target_coherence,
            "action": action,
            "grad_avg": round(grad_avg, 4),
            "reg_mode": reg_mode,
            "mem_recent": round(mem_recent, 4),
            "stable": policy_score >= self.stability_threshold,
            "divergent": policy_score < self.divergence_limit,
        }

    def _mode_score(self, mode: str) -> float:
        """Convert regulation mode to a coherence score."""
        scores = {"exploration": 0.8, "healing": 0.4, "mutation": 0.6}
        return scores.get(mode, 0.5)

    def _determine_action(self, score: float, mode: str, mem: float) -> str:
        """Determine the organism's coherence policy action."""
        if score >= self.target_coherence and "exploration" in mode:
            return "sustain"
        elif score < self.stability_threshold:
            return "regulate"
        elif mem < 0.3 and score < 0.5:
            return "remember"
        elif score > 0.75:
            return "stabilize"
        else:
            return "maintain"


class CoherenceIntegrator:
    """Integrates waves 84-86 into organism-wide coherence decisions."""

    def __init__(self):
        self.policy = CoherencePolicy()
        self.integration_history: List[dict] = []
        self.last_action = "init"
        self.cycle = 0

    def reset(self) -> None:
        """Reset the integrator to initial state."""
        self.policy = CoherencePolicy()
        self.integration_history = []
        self.last_action = "init"
        self.cycle = 0

    def integrate(self, gradient_action: dict, regulation_action: dict, memory_action: dict) -> dict:
        """Integrate actions from all three wave modules."""
        self.cycle += 1

        policy_result = self.policy.evaluate(
            gradient_action.get("hotspots", {}),
            regulation_action,
            memory_action,
        )

        # Record integration
        entry = {
            "cycle": self.cycle,
            "policy_score": policy_result["policy_score"],
            "action": policy_result["action"],
            "grad_contribution": policy_result["grad_avg"],
            "reg_contribution": self.policy._mode_score(regulation_action.get("mode", "healing")),
            "mem_contribution": policy_result["mem_recent"],
            "stable": policy_result["stable"],
            "timestamp": time.time(),
        }
        self.integration_history.append(entry)

        # Keep history manageable
        if len(self.integration_history) > 200:
            self.integration_history = self.integration_history[-100:]

        self.last_action = policy_result["action"]
        return {
            "action": policy_result["action"],
            "policy_score": policy_result["policy_score"],
            "stable": policy_result["stable"],
            "cycle": self.cycle,
            "last_action": self.last_action,
        }

    def get_policy(self) -> dict:
        """Return current coherence policy state."""
        return {
            "target_coherence": self.policy.target_coherence,
            "stability_threshold": self.policy.stability_threshold,
            "divergence_limit": self.policy.divergence_limit,
            "last_action": self.last_action,
            "total_cycles": self.cycle,
            "integration_count": len(self.integration_history),
        }

    def get_integration_timeline(self, last: int = 20) -> List[dict]:
        """Return recent integration history."""
        return self.integration_history[-last:] if self.integration_history else []


def coherence_vitals() -> dict:
    return {"organ": "wave87_coherence_integration", "wave": 87, "status": "active"}


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"policy": CoherencePolicy().__dict__, "history": [], "last_action": "init", "cycle": 0}


def _save(state: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    integrator = CoherenceIntegrator()

    # Restore state
    if state.get("history"):
        integrator.integration_history = state["history"]
    if state.get("last_action"):
        integrator.last_action = state["last_action"]
    if state.get("cycle"):
        integrator.cycle = state["cycle"]
    # Recreate policy from saved dict - can't fully restore but use defaults

    if action == "status":
        policy = integrator.get_policy()
        return {"action": "status", "wave": 87, **policy}

    elif action == "integrate":
        # Expect actions from waves 84-86
        grad_action = req.get("gradient_action", {"action": "status"})
        reg_action = req.get("regulation_action", {"action": "status"})
        mem_action = req.get("memory_action", {"action": "status"})

        result = integrator.integrate(grad_action, reg_action, mem_action)
        # Top-level action is always "integrate" when this action is called
        result["action"] = "integrate"
        state["last_action"] = result["last_action"]
        state["cycle"] = result["cycle"]
        state["history"] = integrator.integration_history
        _save(state)
        return {"action": "integrate", **result}

    elif action == "policy":
        policy = integrator.get_policy()
        return {"action": "policy", **policy}

    elif action == "timeline":
        timeline = integrator.get_integration_timeline()
        return {"action": "timeline", "timeline": timeline}

    elif action == "reset":
        integrator.reset()
        state = {"policy": integrator.policy.__dict__, "history": integrator.integration_history,
                 "last_action": integrator.last_action, "cycle": integrator.cycle}
        _save(state)
        return {"action": "reset", "reset": True}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    result = handler({"action": action})
    print(json.dumps(result, indent=2, default=str))
