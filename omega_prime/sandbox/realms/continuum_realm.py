from typing import Any

from ...nucleus.interfaces.sandbox_port import SandboxPort
from ..modules.physics_engine import PhysicsEngine


class ContinuumRealm(SandboxPort):
    """Continuous-space realm with physics integration."""

    def __init__(self) -> None:
        self._bodies: dict[str, tuple[list[float], list[float]]] = {}
        self._time = 0.0
        self._physics = PhysicsEngine()

    def materialize(self, config: dict[str, Any]) -> None:
        self._bodies = {
            bid: (body.get("position", [0.0, 0.0]), body.get("velocity", [0.0, 0.0]))
            for bid, body in config.get("bodies", {}).items()
        }
        self._time = 0.0

    def advance(self, intents: list[dict[str, Any]]) -> dict[str, Any]:
        self._time += 1.0
        for intent in intents:
            bid = intent.get("body_id")
            if bid in self._bodies:
                pos, vel = self._bodies[bid]
                new_pos, new_vel = self._physics.integrate(pos, vel)
                self._bodies[bid] = (new_pos, new_vel)
        return {"t": self._time, "bodies": len(self._bodies)}

    @property
    def observation(self) -> dict[str, Any]:
        return {"realm": "continuum", "t": self._time,
                "bodies": {bid: pos for bid, (pos, _) in self._bodies.items()}}

    def dissolve(self) -> None:
        self._bodies.clear()
