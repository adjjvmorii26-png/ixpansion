import random
from typing import Any

from ..modules.physics import PhysicsEngine
from core.interfaces.sandbox_interface import SandboxInterface
from core.utils.logging import get_logger

logger = get_logger(__name__)


class GridWorld(SandboxInterface):
    """Discrete 2D grid environment with agent positions."""

    def __init__(self, width: int = 20, height: int = 20) -> None:
        self.width = width
        self.height = height
        self._grid: dict[tuple[int, int], dict[str, Any]] = {}
        self._physics = PhysicsEngine()
        self._tick = 0

    def setup(self, config: dict[str, Any]) -> None:
        self.width = config.get("width", self.width)
        self.height = config.get("height", self.height)
        for x in range(self.width):
            for y in range(self.height):
                self._grid[(x, y)] = {
                    "terrain": random.choice(["plains", "forest", "rock"]),
                    "explored": False,
                    "agents": [],
                }
        logger.info("grid world initialized %dx%d", self.width, self.height)

    def step(self, actions: list[dict[str, Any]]) -> dict[str, Any]:
        self._tick += 1
        results = []
        for action in actions:
            if action.get("action") == "move":
                target = action.get("target")
                if target and target in self._grid:
                    self._grid[target]["explored"] = True
                    results.append({"agent": action.get("agent"), "moved_to": target})
            else:
                results.append({"agent": action.get("agent"), "status": "noop"})
        return {"tick": self._tick, "results": results}

    def reset(self) -> dict[str, Any]:
        self._tick = 0
        for cell in self._grid.values():
            cell["explored"] = False
            cell["agents"] = []
        return {"observation": {str(k): v for k, v in self._grid.items()}}

    def teardown(self) -> None:
        self._grid.clear()
        logger.info("grid world torn down")

    @property
    def observation(self) -> dict[str, Any]:
        return {str(k): {"explored": v["explored"], "terrain": v["terrain"]} for k, v in self._grid.items()}
