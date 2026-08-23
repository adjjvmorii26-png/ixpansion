from typing import Any


class GoalStack:
    def __init__(self) -> None:
        self._stack: list[dict[str, Any]] = []

    def push(self, goal: dict[str, Any]) -> None:
        self._stack.append(goal)

    def pop(self) -> dict[str, Any] | None:
        return self._stack.pop() if self._stack else None

    @property
    def depth(self) -> int:
        return len(self._stack)

    def derive_plan(self) -> list[dict[str, Any]]:
        if not self._stack:
            return []
        top = self._stack[-1]
        return [
            {"phase": "recon", "target": top.get("target", "")},
            {"phase": "act", "strategy": top.get("strategy", "direct")},
            {"phase": "verify"},
        ]
