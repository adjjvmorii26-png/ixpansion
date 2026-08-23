from typing import Any

from ..base.agent_base import AgentBase
from ..cognition.planning import GoalStack


class Architect(AgentBase):
    """Builder species: designs structures, plans construction."""

    def __init__(self, agent_id: str) -> None:
        super().__init__(agent_id, species="architect")
        self._goals = GoalStack()

    def awaken(self, config: dict[str, Any]) -> None:
        super().awaken(config)
        for g in config.get("blueprints", []):
            self._goals.push(g)

    def deliberate(self) -> dict[str, Any]:
        plan = self._goals.derive_plan()
        return {"intent": "construct", "plan": plan} if plan else {"intent": "idle"}
