import random
from typing import Any

from ..base.agent_base import AgentBase
from ..cognition.memory_cells import MemoryCells


class Wanderer(AgentBase):
    """Explorer species: roams, maps terrain, remembers landmarks."""

    def __init__(self, agent_id: str) -> None:
        super().__init__(agent_id, species="wanderer")
        self._memory = MemoryCells(capacity=64)

    def deliberate(self) -> dict[str, Any]:
        known = set()
        for key in range(64):
            val = self._memory.recall(f"cell_{key}")
            if val:
                known.add(val)
        directions = ["north", "south", "east", "west"]
        choice = random.choice(directions)
        return {"intent": "move", "direction": choice}
