"""Wave 120 — Self-Observe Engine.

Meta-cognitive recursive observation: watches the watcher watching itself.
Creates observation chains where each layer records what the previous
layer detected, enabling the system to reflect on its own reflection.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class ObservationLayer:
    """A single recursive observation layer."""

    def __init__(self, depth: int, target: str, payload: Optional[Any] = None):
        self.depth = depth
        self.target = target
        self.payload = payload or {}
        self.timestamp = time.time()
        self.children: List[ObservationLayer] = []

    def add_child(self, target: str, payload: Optional[Any] = None) -> "ObservationLayer":
        child = ObservationLayer(depth=self.depth + 1, target=target, payload=payload)
        self.children.append(child)
        return child

    def to_dict(self) -> Dict[str, Any]:
        return {
            "depth": self.depth,
            "target": self.target,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "children": [c.to_dict() for c in self.children],
        }

    def total_nodes(self) -> int:
        return 1 + sum(c.total_nodes() for c in self.children)


class SelfObserveEngine:
    """Recursive meta-cognitive observation engine."""

    def __init__(self, max_depth: int = 7):
        self.max_depth = max_depth
        self._roots: List[ObservationLayer] = []
        self._observation_count = 0

    def begin_observation(self, target: str) -> ObservationLayer:
        root = ObservationLayer(depth=0, target=target, payload={"origin": "self_observe"})
        self._roots.append(root)
        self._observation_count += 1
        return root

    def reflect(self, layer: ObservationLayer) -> ObservationLayer:
        if layer.depth >= self.max_depth:
            return layer
        child = layer.add_child(
            target=f"reflection_of_{layer.target}",
            payload={"reflected_at": time.time(), "depth": layer.depth + 1},
        )
        self._observation_count += 1
        return child

    def deep_observe(self, target: str, depth: int = 0) -> ObservationLayer:
        layer = self.begin_observation(target)
        current = layer
        for d in range(min(depth, self.max_depth)):
            current = self.reflect(current)
        return layer

    def get_all_roots(self) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self._roots]

    def status(self) -> Dict[str, Any]:
        total_nodes = sum(r.total_nodes() for r in self._roots)
        return {
            "observation_count": self._observation_count,
            "total_roots": len(self._roots),
            "total_nodes": total_nodes,
            "max_depth": self.max_depth,
        }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "self_observe_engine", "action": action}
