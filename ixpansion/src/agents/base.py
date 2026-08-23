from __future__ import annotations
from typing import Any


class Agent:
    name = "base"
    temperament = "neutral"

    def act(self, perception: dict[str, Any]) -> list[dict[str, Any]]:
        return [{"type": "observe", "node": perception.get("focus", "origin"), "value": perception.get("tick", 0)}]
