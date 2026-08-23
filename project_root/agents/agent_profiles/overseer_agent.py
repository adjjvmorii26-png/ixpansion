from typing import Any

from ..base_agent import BaseAgent
from ..behaviors.planning import Planner


class OverseerAgent(BaseAgent):
    """Coordinates other agents, allocates tasks, monitors system health."""

    def __init__(self, agent_id: str, **kwargs: Any) -> None:
        super().__init__(agent_id, name="Overseer")
        self._planner = Planner()

    def initialize(self, config: dict[str, Any]) -> None:
        super().initialize(config)
        for goal in config.get("initial_goals", []):
            self._planner.push_goal(goal)

    def decide(self) -> dict[str, Any]:
        plan = self._planner.plan(self._observation)
        return {"action": "coordinate", "plan": plan}
