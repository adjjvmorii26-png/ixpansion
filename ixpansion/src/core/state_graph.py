from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Node:
    id: str
    kind: str = "region"
    state: dict[str, Any] = field(default_factory=dict)


class StateGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: set[tuple[str, str, str]] = set()

    def add_node(self, node_id: str, kind: str = "region", **state: Any) -> Node:
        if node_id in self.nodes:
            raise ValueError(f"duplicate node: {node_id}")
        node = Node(node_id, kind, dict(state))
        self.nodes[node_id] = node
        return node

    def connect(self, source: str, target: str, relation: str = "adjacent") -> None:
        if source not in self.nodes or target not in self.nodes:
            raise KeyError("both nodes must exist before connecting")
        self.edges.add((source, target, relation))

    def neighbors(self, node_id: str, relation: str | None = None) -> list[str]:
        return [target for source, target, edge in self.edges if source == node_id and relation in (None, edge)]

    def fingerprint(self) -> str:
        payload = {
            "nodes": {key: {"kind": value.kind, "state": value.state} for key, value in sorted(self.nodes.items())},
            "edges": sorted(self.edges),
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
