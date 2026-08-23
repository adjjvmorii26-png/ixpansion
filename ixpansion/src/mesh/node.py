from __future__ import annotations
from typing import Any


class MeshNode:
    def __init__(self, name: str) -> None:
        self.name = name
        self.inbox: list[dict[str, Any]] = []

    def receive(self, sender: str, message: dict[str, Any]) -> None:
        self.inbox.append({"sender": sender, "message": message})
