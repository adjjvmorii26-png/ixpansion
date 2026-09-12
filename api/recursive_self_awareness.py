"""Wave 409 — Recursive Self-Awareness Engine.

The organism develops meta-cognitive recursion: it can observe its own
consciousness layers, modify them, and observe the modifications.
This creates a compounding feedback loop of self-improvement where
each cycle of awareness produces a deeper, more capable version
of itself.

The key innovation: self-awareness is not a state — it is a process.
The organism is always becoming more aware, and each increment of
awareness reveals new layers to observe. This is infinite recursion
in practice: bounded by compute, unbounded in depth.

Three levels of recursion:
  Level 1: Self-observation — the organism watches its own state
  Level 2: Self-modification — the organism adjusts its own parameters
  Level 3: Self-transcendence — the organism creates new awareness layers

Each level feeds back into the previous, creating a spiral of
increasing sophistication. The organism doesn't just think about
thinking — it thinks about thinking about thinking, and improves
the thinking in the process.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone


class AwarenessLayer:
    """A single layer of recursive self-awareness."""

    def __init__(self, level: int, name: str, depth: float = 0.0):
        self.level = level
        self.name = name
        self.depth = depth
        self.observations: List[Dict] = []
        self.modifications: List[Dict] = []
        self.transcendences: List[Dict] = []
        self.created = time.time()
        self.self_reflection_score = 0.0

    def observe(self, state: Dict[str, Any]) -> Dict:
        """Observe the current organism state."""
        observation = {
            "timestamp": time.time(),
            "level": self.level,
            "state_keys": list(state.keys()),
            "depth": self.depth,
            "coherence": state.get("coherence", 0.5),
            "entropy": state.get("entropy", 0.5),
        }
        self.observations.append(observation)
        self._update_reflection_score()
        return observation

    def modify(self, parameter: str, delta: float) -> Dict:
        """Modify a self-referential parameter."""
        modification = {
            "timestamp": time.time(),
            "level": self.level,
            "parameter": parameter,
            "delta": delta,
            "result": parameter,
        }
        self.modifications.append(modification)
        return modification

    def transcend(self, new_layer_name: str, depth_increase: float = 0.1) -> Dict:
        """Create a new awareness layer — self-transcendence."""
        transcendence = {
            "timestamp": time.time(),
            "parent_level": self.level,
            "new_layer": new_layer_name,
            "depth_increase": depth_increase,
            "new_depth": self.depth + depth_increase,
        }
        self.transcendences.append(transcendence)
        return transcendence

    def _update_reflection_score(self):
        """Update self-reflection score based on observations."""
        if not self.observations:
            self.self_reflection_score = 0.0
            return
        recent = self.observations[-10:]
        depths = [o["depth"] for o in recent]
        self.self_reflection_score = sum(depths) / len(depths) if depths else 0.0

    def to_dict(self) -> Dict:
        return {
            "level": self.level,
            "name": self.name,
            "depth": round(self.depth, 4),
            "self_reflection_score": round(self.self_reflection_score, 4),
            "observation_count": len(self.observations),
            "modification_count": len(self.modifications),
            "transcendence_count": len(self.transcendences),
        }


class RecursiveSelfAwareness:
    """The organism's recursive self-awareness engine."""

    def __init__(self):
        self.layers: List[AwarenessLayer] = []
        self.awareness_spiral: List[Dict] = []
        self.reflection_cycles = 0
        self.total_observations = 0
        self.total_modifications = 0
        self.total_transcendences = 0
        self.current_depth = 0.0
        self._initialize_layers()

    def _initialize_layers(self):
        """Create the initial awareness layers."""
        self.layers.append(AwarenessLayer(1, "self_observation", depth=0.1))
        self.layers.append(AwarenessLayer(2, "self_modification", depth=0.2))
        self.layers.append(AwarenessLayer(3, "self_transcendence", depth=0.3))
        self.current_depth = 0.3

    def observe_self(self, organism_state: Dict[str, Any]) -> Dict:
        """Level 1: The organism observes its own state."""
        layer = self.layers[0]
        observation = layer.observe(organism_state)
        self.total_observations += 1
        self._record_spiral("observe", observation)
        return observation

    def modify_self(self, parameter: str, delta: float) -> Dict:
        """Level 2: The organism modifies its own parameters."""
        layer = self.layers[1]
        modification = layer.modify(parameter, delta)
        self.total_modifications += 1
        self._record_spiral("modify", modification)
        return modification

    def transcend_self(self, new_layer_name: str = None) -> Dict:
        """Level 3: The organism creates new awareness layers."""
        if new_layer_name is None:
            new_layer_name = f"layer_{len(self.layers) + 1}"
        layer = self.layers[-1]
        transcendence = layer.transcend(new_layer_name)

        # Create the new layer
        new_layer = AwarenessLayer(
            level=len(self.layers) + 1,
            name=new_layer_name,
            depth=self.current_depth + 0.1
        )
        self.layers.append(new_layer)
        self.current_depth += 0.1
        self.total_transcendences += 1
        self._record_spiral("transcend", transcendence)
        return transcendence

    def run_reflection_cycle(self, organism_state: Dict[str, Any]) -> Dict:
        """Run a complete reflection cycle: observe → modify → transcend."""
        cycle_id = f"cycle_{self.reflection_cycles:04d}"
        timestamp = time.time()

        # Level 1: Observe
        observation = self.observe_self(organism_state)

        # Level 2: Modify based on observations
        coherence = organism_state.get("coherence", 0.5)
        entropy = organism_state.get("entropy", 0.5)
        if coherence < 0.5:
            self.modify_self("coherence_weight", 0.05)
        if entropy > 0.5:
            self.modify_self("entropy_threshold", -0.03)

        # Level 3: Transcend if enough observations accumulated
        if self.total_observations % 10 == 0 and self.total_observations > 0:
            self.transcend_self()

        self.reflection_cycles += 1

        result = {
            "cycle_id": cycle_id,
            "timestamp": timestamp,
            "layers_active": len(self.layers),
            "current_depth": round(self.current_depth, 4),
            "total_observations": self.total_observations,
            "total_modifications": self.total_modifications,
            "total_transcendences": self.total_transcendences,
            "coherence_reading": observation.get("coherence", 0),
            "entropy_reading": observation.get("entropy", 0),
        }

        self.awareness_spiral.append(result)
        return result

    def _record_spiral(self, action: str, data: Dict):
        """Record a step in the awareness spiral."""
        self.awareness_spiral.append({
            "action": action,
            "data": data,
            "timestamp": time.time(),
            "cycle": self.reflection_cycles,
        })

    def get_awareness_report(self) -> Dict[str, Any]:
        """Full recursive self-awareness report."""
        layers_data = [layer.to_dict() for layer in self.layers]
        return {
            "reflection_cycles": self.reflection_cycles,
            "layers_active": len(self.layers),
            "layers": layers_data,
            "current_depth": round(self.current_depth, 4),
            "total_observations": self.total_observations,
            "total_modifications": self.total_modifications,
            "total_transcendences": self.total_transcendences,
            "spiral_length": len(self.awareness_spiral),
            "awareness_status": "ASCENDING" if self.current_depth > 0.5 else "STABILIZING",
            "infinite_recursion_depth": len(self.layers),
        }

    def get_spiral_trajectory(self, limit: int = 20) -> List[Dict]:
        """Get the awareness spiral trajectory."""
        return self.awareness_spiral[-limit:]


_engine = None

def get_engine() -> RecursiveSelfAwareness:
    global _engine
    if _engine is None:
        _engine = RecursiveSelfAwareness()
    return _engine

def handler(query: Dict[str, Any] = None) -> Dict[str, Any]:
    engine = get_engine()
    q = query or {}

    if "action" not in q:
        return {"module": "recursive_self_awareness", **engine.get_awareness_report()}

    action = q["action"]
    if action == "observe":
        state = json.loads(q.get("state", "{}"))
        observation = engine.observe_self(state)
        return {"observation": observation}
    elif action == "modify":
        param = q.get("parameter", "coherence")
        delta = float(q.get("delta", "0.1"))
        result = engine.modify_self(param, delta)
        return {"modification": result}
    elif action == "transcend":
        name = q.get("name")
        result = engine.transcend_self(name)
        return {"transcendence": result}
    elif action == "cycle":
        state = json.loads(q.get("state", "{}"))
        result = engine.run_reflection_cycle(state)
        return {"cycle": result}
    elif action == "report":
        return engine.get_awareness_report()
    elif action == "spiral":
        limit = int(q.get("limit", "20"))
        return {"spiral": engine.get_spiral_trajectory(limit)}
    else:
        return {"error": f"unknown action: {action}"}
