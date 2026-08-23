from dataclasses import dataclass
from typing import Any


@dataclass
class Node:
    name: str
    stock: float
    flow_rate: float = 0.0


class ResourceFlow:
    """Directed resource graph with decay and transfer."""

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._edges: dict[str, str] = {}

    def add_node(self, name: str, initial_stock: float, flow_rate: float = 1.0) -> None:
        self._nodes[name] = Node(name=name, stock=initial_stock, flow_rate=flow_rate)

    def connect(self, src: str, dst: str) -> None:
        self._edges[src] = dst

    def tick(self) -> None:
        for src_name, dst_name in self._edges.items():
            src = self._nodes.get(src_name)
            dst = self._nodes.get(dst_name)
            if src and dst and src.stock > 0:
                amount = min(src.flow_rate, src.stock)
                src.stock -= amount
                dst.stock += amount

    def levels(self) -> dict[str, float]:
        return {n.name: n.stock for n in self._nodes.values()}
