from __future__ import annotations
from typing import Any
from agents.base import Agent


class Architect(Agent):
    name = "architect"
    temperament = "constructive"

    def act(self, perception: dict[str, Any]) -> list[dict[str, Any]]:
        tick = int(perception.get("tick", 0))
        return [{"type": "spawn", "node": f"spire-{tick}", "kind": perception.get("scene", "structure")}]
