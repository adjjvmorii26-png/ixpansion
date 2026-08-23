from typing import Any

from ..base_agent import BaseAgent
from ..behaviors.memory import MemoryBuffer


class ScoutAgent(BaseAgent):
    """Explores the sandbox, discovers new regions, reports findings."""

    def __init__(self, agent_id: str, **kwargs: Any) -> None:
        super().__init__(agent_id, name="Scout")
        self._memory = MemoryBuffer(capacity=128)

    def decide(self) -> dict[str, Any]:
        unseen = [
            cell for cell, info in self._observation.get("grid", {}).items()
            if not info.get("explored", False)
        ]
        if not unseen:
            return {"action": "idle"}
        target = unseen[0]
        return {"action": "move", "target": target}
