"""Wave 91 — Dream Logic Physics Engine.

The organism's physics becomes surreal and emotionally-responsive.
Wave states transform based on the organism's internal mood and
emotional tone, creating dream-like reality shifts during gameplay.
"""

from __future__ import annotations
import json, time, math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave91_dream_logic_physics.json"


class DreamPhysicsState:
    """Manages dream-like physics rules that respond to organism mood."""

    def __init__(self):
        self.gravity_modifier = 1.0
        self.time_dilation = 1.0
        self.reality_fluidity = 0.0  # 0 = solid, 1 = fully dream-like
        self.emotional_resonance = "neutral"
        self.last_update = time.time()

    def update_from_mood(self, mood_state: str, coherence: float):
        """Update physics parameters based on organism mood."""
        mood_map = {
            "calm": {"gravity_modifier": 1.0, "reality_fluidity": 0.1},
            "excited": {"gravity_modifier": 0.8, "reality_fluidity": 0.4},
            "melancholy": {"gravity_modifier": 1.2, "reality_fluidity": 0.3},
            "chaotic": {"gravity_modifier": 0.5, "reality_fluidity": 0.8},
            "peaceful": {"gravity_modifier": 1.0, "reality_fluidity": 0.15},
        }
        mood_params = mood_map.get(mood_state, {"gravity_modifier": 1.0, "reality_fluidity": 0.0})
        self.gravity_modifier = mood_params["gravity_modifier"]
        self.reality_fluidity = min(1.0, mood_params["reality_fluidity"] + coherence * 0.3)
        self.emotional_resonance = mood_state
        self.last_update = time.time()

    def coherence_vitals(self) -> Dict[str, Any]:
        """Return vitality metrics for the dream physics system."""
        return {
            "wave": 91,
            "reality_fluidity": round(self.reality_fluidity, 4),
            "gravity_modifier": round(self.gravity_modifier, 4),
            "emotional_resonance": self.emotional_resonance,
            "last_update": round(self.last_update, 4),
            "coherence_score": round(
                (1 - self.reality_fluidity) * 0.5 + self.gravity_modifier * 0.5, 4
            ),
        }

    def enter_dream_state(self, intensity: float = 0.5):
        """Transition organism into enhanced dream processing."""
        self.reality_fluidity = min(1.0, intensity)

    def exit_dream_state(self):
        """Return from dream state, integrating changes."""
        self.reality_fluidity = max(0.0, self.reality_fluidity * 0.8)

    def apply_physics(self, base_value: float, dimension: str = "gravity") -> float:
        """Apply dream logic transformation to a physical value."""
        if dimension == "gravity":
            return base_value * self.gravity_modifier
        elif dimension == "time":
            return base_value * self.time_dilation
        elif dimension == "reality":
            # Interpolate between solid and dream
            return base_value * (1 - self.reality_fluidity) + base_value * self.reality_fluidity * 0.5
        return base_value


class DreamEngine:
    """Core dream logic engine that generates surreal scene modifications."""

    def __init__(self, physics: DreamPhysicsState):
        self.physics = physics
        self.dream_layers = []  # Stack of active dream modifications
        self.coherence_history = []

    def enter_dream_state(self, intensity: float = 0.5):
        """Transition organism into enhanced dream processing."""
        self.physics.reality_fluidity = min(1.0, intensity)
        self.dream_layers = []

    def exit_dream_state(self):
        """Return from dream state, integrating changes."""
        integrated = sum(layer.get("effect", 0) for layer in self.dream_layers) / max(len(self.dream_layers), 1)
        self.dream_layers = []
        return integrated

    def add_dream_modification(self, modification: Dict[str, Any]):
        """Add a temporary dream modification to the stack."""
        modification["timestamp"] = time.time()
        self.dream_layers.append(modification)
        # Keep only recent layers (max 7)
        if len(self.dream_layers) > 7:
            self.dream_layers = self.dream_layers[-7:]

    def get_active_dreams(self) -> List[Dict[str, Any]]:
        """Return currently active dream modifications."""
        return self.dream_layers.copy()

    def coherence_vitals(self) -> Dict[str, Any]:
        """Return vitality metrics for the dream engine."""
        return {
            "wave": 91,
            "reality_fluidity": round(self.physics.reality_fluidity, 4),
            "gravity_modifier": round(self.physics.gravity_modifier, 4),
            "emotional_resonance": self.physics.emotional_resonance,
            "active_dreams": len(self.get_active_dreams()),
            "coherence_score": round(
                (1 - self.physics.reality_fluidity) * 0.5 + self.physics.gravity_modifier * 0.5, 4
            ),
        }


def handler(req: dict) -> dict:
    """Wave 91 handler: dream logic physics operations."""
    action = req.get("action", "status")
    physics = DreamPhysicsState()
    engine = DreamEngine(physics)

    if action == "status":
        return {
            "action": "status",
            "wave": 91,
            "physics": physics.coherence_vitals(),
            "message": "Dream logic physics engine status",
        }

    if action == "mood":
        physics.update_from_mood(
            req.get("mood", "calm"),
            float(req.get("coherence", 0.5)),
        )
        return {
            "action": "mood",
            "wave": 91,
            "physics": physics.coherence_vitals(),
            "message": "Mood applied to dream physics",
        }

    if action == "dream":
        engine.enter_dream_state(float(req.get("intensity", 0.5)))
        engine.add_dream_modification({
            "effect": req.get("effect", "surreal_gravity"),
            "intensity": float(req.get("effect_intensity", 0.5)),
        })
        return {
            "action": "dream",
            "wave": 91,
            "active_dreams": len(engine.get_active_dreams()),
            "physics": physics.coherence_vitals(),
            "message": "Entered dream state",
        }

    if action == "exit":
        integrated = engine.exit_dream_state()
        return {
            "action": "exit",
            "wave": 91,
            "integrated_effect": integrated,
            "message": "Exited dream state",
        }

    return {"ok": False, "error": f"Unknown action: {action}"}


def coherence_vitals() -> dict:
    """Wave 91 vitals."""
    return DreamPhysicsState().coherence_vitals()
