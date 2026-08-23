from typing import Any

from core.interfaces.sandbox_interface import SandboxInterface


class SimulationSpace(SandboxInterface):
    """Continuous-space simulation with entity positions and velocities."""

    def __init__(self) -> None:
        self._entities: dict[str, dict[str, Any]] = {}
        self._time: float = 0.0

    def setup(self, config: dict[str, Any]) -> None:
        self._entities = config.get("initial_entities", {})
        self._time = 0.0

    def step(self, actions: list[dict[str, Any]]) -> dict[str, Any]:
        self._time += 1.0
        for action in actions:
            eid = action.get("entity_id")
            if eid in self._entities:
                vel = action.get("velocity", [0.0, 0.0])
                pos = self._entities[eid].get("position", [0.0, 0.0])
                self._entities[eid]["position"] = [
                    pos[0] + vel[0],
                    pos[1] + vel[1],
                ]
        return {"time": self._time, "entities": len(self._entities)}

    def reset(self) -> dict[str, Any]:
        self._time = 0.0
        return {"observation": self._entities}

    def teardown(self) -> None:
        self._entities.clear()
