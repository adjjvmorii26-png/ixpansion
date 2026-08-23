from __future__ import annotations
from typing import Any

from mesh.node import MeshNode


class MeshChannels:
    def __init__(self, edges: list[tuple[str, str, str]]) -> None:
        names = sorted({name for edge in edges for name in edge[:2]})
        self.nodes = {name: MeshNode(name) for name in names}
        self.edges = edges

    def broadcast(self, sender: str, message: dict[str, Any]) -> int:
        delivered = 0
        for source, target, _relation in self.edges:
            if source == sender and target != sender:
                self.nodes[target].receive(sender, message)
                delivered += 1
        return delivered

    def inbox_count(self, node: str) -> int:
        return len(self.nodes[node].inbox)
