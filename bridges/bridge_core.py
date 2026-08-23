"""BridgeHub — unified interface connecting all three engine projects.

This module imports from omega_prime, omega_fractal_engine, and
project_root simultaneously, creating a meta-system where events,
emotions, and entropy flow between previously isolated engines.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root / "project_root"))

# omega_prime imports (already on path via workspace root)
from omega_prime.nucleus.kernel.state_core import StateCore
from omega_prime.nucleus.kernel.reactor import Reactor

# fractal_engine imports
from omega_fractal_engine.nucleus.kernel.entropy_regulator import EntropyRegulator
from omega_fractal_engine.nucleus.identity.mood_vectors import MoodEngine

# project_root imports
from nucleus.sandbox.event_mesh import EventMesh


class BridgeHub:
    """Central orchestrator connecting all three engines."""

    def __init__(self, seed: int | None = None) -> None:
        self.state_core = StateCore()
        self.reactor = Reactor()
        self.entropy_regulator = EntropyRegulator()
        self.mood_engine = MoodEngine(volatility=0.2)
        self.event_mesh = EventMesh()

        # Wire event mesh → reactor
        for layer in ["physical", "social", "economic", "cultural", "meta"]:
            self.event_mesh.subscribe(layer, self._mesh_to_reactor)

    def _mesh_to_reactor(self, event: dict[str, Any]) -> None:
        """Forward project_root events into omega_prime's reactor."""
        import asyncio
        try:
            asyncio.get_running_loop().create_task(
                self.reactor.emit(event.get("event", "unknown"), event)
            )
        except RuntimeError:
            return

    def set_state(self, key: str, value: dict[str, Any]) -> None:
        """Write to omega_prime's global state."""
        self.state_core.set(key, value)

    def get_state(self, path: str) -> Any:
        return self.state_core.get(path)

    def propagate_emotion(self, agent_id: str) -> dict[str, Any]:
        """Read emotional data from state_core and feed into fractal_engine's mood."""
        raw = self.state_core.get(agent_id, {})
        if not raw:
            return {}

        # Map omega_prime's atom into fractal_engine's affect vector.
        self.mood_engine.mood.valence = max(
            -1.0, min(1.0, float(raw.get("valence", 0.0)))
        )
        self.mood_engine.mood.arousal = max(
            0.0, min(1.0, float(raw.get("arousal", 0.5)))
        )
        event = {
            "tick": len(self.mood_engine.history_labels) + 1,
            "valence": self.mood_engine.mood.valence,
            "arousal": self.mood_engine.mood.arousal,
        }
        label = self.mood_engine.process(event)
        return {"mood": label, "source_agent": agent_id}

    def route_event(self, layer: str, event_type: str, payload: dict[str, Any]) -> dict[str, int]:
        """Publish through project_root's mesh; returns delivery stats."""
        delivered = self.event_mesh.publish(layer, event_type, payload)
        return {"delivered": delivered, "layer": layer}

    def get_chaos_level(self) -> float:
        """Read current chaos from fractal_engine's regulator."""
        result = self.entropy_regulator.regulate()
        return result["current"]

    @property
    def status(self) -> dict[str, Any]:
        return {
            "state_keys": len(self.state_core.raw),
            "reactor_events": len(self.reactor.events),
            "chaos": round(self.entropy_regulator.current_entropy, 4),
            "mood": self.mood_engine.current_label,
            "mesh_events": self.event_mesh.total_events,
        }
