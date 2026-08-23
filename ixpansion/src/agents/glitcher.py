from __future__ import annotations
from typing import Any
from agents.base import Agent


class Glitcher(Agent):
    name = "glitcher"
    temperament = "chaotic"

    def act(self, perception: dict[str, Any]) -> list[dict[str, Any]]:
        if int(perception.get("tick", 0)) % 3 != 0:
            return []
        return [{"type": "anomaly", "node": perception.get("focus", "origin"), "value": "identity-split"}]
