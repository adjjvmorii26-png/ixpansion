from __future__ import annotations
from typing import Any
from agents.base import Agent


class Observer(Agent):
    name = "observer"
    temperament = "calm"

    def act(self, perception: dict[str, Any]) -> list[dict[str, Any]]:
        return [{"type": "record", "node": perception.get("focus", "origin"), "fingerprint": perception.get("fingerprint")}]
