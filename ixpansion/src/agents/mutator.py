from __future__ import annotations
from typing import Any
from agents.base import Agent


class Mutator(Agent):
    name = "mutator"
    temperament = "adaptive"

    def act(self, perception: dict[str, Any]) -> list[dict[str, Any]]:
        focus = str(perception.get("focus", "origin"))
        return [{"type": "mutate", "node": focus, "field": "energy", "operation": "add", "value": 2}]
