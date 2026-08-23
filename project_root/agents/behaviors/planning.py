from typing import Any


class Planner:
    """Simple goal-stack planner."""

    def __init__(self) -> None:
        self._goals: list[dict[str, Any]] = []

    def push_goal(self, goal: dict[str, Any]) -> None:
        self._goals.append(goal)

    def pop_goal(self) -> dict[str, Any] | None:
        return self._goals.pop() if self._goals else None

    @property
    def has_goals(self) -> bool:
        return bool(self._goals)

    def plan(self, current_state: dict[str, Any]) -> list[dict[str, Any]]:
        if not self._goals:
            return []
        goal = self._goals[-1]
        return [
            {"step": 1, "action": "assess", "target": goal.get("target", "")},
            {"step": 2, "action": "execute", "strategy": goal.get("strategy", "default")},
        ]
