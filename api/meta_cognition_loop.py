"""Wave 121 — Meta-Cognition Loop.

Three nested layers of thinking about thinking about thinking.
Each layer observes the one below it, creating a tower of
self-referential awareness that can resolve paradoxes through
transcendence.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class CognitiveLayer:
    """A single layer of meta-cognition."""

    def __init__(self, level: int, description: str = ""):
        self.level = level
        self.description = description
        self.insights: List[str] = []
        self.observed_at: float = time.time()
        self.children: List["CognitiveLayer"] = []

    def think(self, insight: str) -> None:
        self.insights.append(insight)

    def observe(self, child: "CognitiveLayer") -> None:
        self.children.append(child)

    def total_insights(self) -> int:
        return len(self.insights) + sum(c.total_insights() for c in self.children)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "description": self.description,
            "insights": self.insights,
            "children": [c.to_dict() for c in self.children],
        }


class MetaCognitionLoop:
    """Manages nested layers of meta-cognition."""

    MAX_LEVELS = 7

    def __init__(self):
        self._loops: List[CognitiveLayer] = []
        self._resolution_count = 0

    def begin_thinking(self, description: str = "base") -> CognitiveLayer:
        layer = CognitiveLayer(level=0, description=description)
        self._loops.append(layer)
        return layer

    def ascend(self, parent: CognitiveLayer, description: str = "") -> CognitiveLayer:
        if parent.level >= self.MAX_LEVELS:
            return parent
        child = CognitiveLayer(level=parent.level + 1, description=description)
        parent.observe(child)
        return child

    def build_tower(self, depth: int = 3, description: str = "tower") -> CognitiveLayer:
        root = self.begin_thinking(description)
        current = root
        for d in range(1, depth + 1):
            current = self.ascend(current, f"meta_level_{d}")
        return root

    def resolve(self, layer: CognitiveLayer, resolution: str) -> Dict[str, Any]:
        layer.think(f"RESOLVED: {resolution}")
        self._resolution_count += 1
        return {
            "level": layer.level,
            "resolution": resolution,
            "timestamp": time.time(),
        }

    def status(self) -> Dict[str, Any]:
        total_insights = sum(l.total_insights() for l in self._loops)
        return {
            "active_loops": len(self._loops),
            "total_insights": total_insights,
            "resolutions": self._resolution_count,
            "max_level": self.MAX_LEVELS,
        }
