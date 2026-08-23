import random
from typing import Any

from ...nucleus.interfaces.sandbox_port import SandboxPort


class LatticeRealm(SandboxPort):
    """Discrete grid world with terrain and explored flags."""

    def __init__(self, size: int = 16) -> None:
        self.size = size
        self._cells: dict[tuple[int, int], str] = {}

    def materialize(self, config: dict[str, Any]) -> None:
        self.size = config.get("size", self.size)
        terrains = ["plains", "crystal", "void", "ember"]
        for x in range(self.size):
            for y in range(self.size):
                self._cells[(x, y)] = random.choice(terrains)

    def advance(self, intents: list[dict[str, Any]]) -> dict[str, Any]:
        moved = sum(1 for i in intents if i.get("intent") == "move")
        return {"moved": moved, "total": len(intents)}

    @property
    def observation(self) -> dict[str, Any]:
        return {"realm": "lattice", "size": self.size, "terrain_sample": random.choice(list(self._cells.values())) if self._cells else None}

    def dissolve(self) -> None:
        self._cells.clear()
