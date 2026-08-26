"""Wave 121 — Fractal Memory Plaza.

Memory structures that are self-similar at every scale: zoom into any
memory and find another complete memory plaza, creating infinite depth
of recall with constant structure.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class MemoryCell:
    """A self-similar memory unit."""

    def __init__(self, label: str, data: Any = None, depth: int = 0):
        self.label = label
        self.data = data
        self.depth = depth
        self.created = time.time()
        self.id = hashlib.sha256(f"{label}:{depth}".encode()).hexdigest()[:10]
        self.children: List["MemoryCell"] = []
        self.access_count = 0

    def access(self) -> Any:
        self.access_count += 1
        return self.data

    def nest(self, label: str, data: Any = None) -> "MemoryCell":
        child = MemoryCell(label=label, data=data, depth=self.depth + 1)
        self.children.append(child)
        return child

    def total_cells(self) -> int:
        return 1 + sum(c.total_cells() for c in self.children)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "depth": self.depth,
            "access_count": self.access_count,
            "children_count": len(self.children),
        }


class FractalMemoryPlaza:
    """Self-similar memory structure at every scale."""

    def __init__(self):
        self._roots: List[MemoryCell] = []
        self._recall_count = 0

    def create_plaza(self, label: str, data: Any = None) -> MemoryCell:
        cell = MemoryCell(label=label, data=data)
        self._roots.append(cell)
        return cell

    def recall(self, cell_id: str) -> Optional[MemoryCell]:
        for root in self._roots:
            found = self._find(root, cell_id)
            if found:
                found.access()
                self._recall_count += 1
                return found
        return None

    def _find(self, cell: MemoryCell, cell_id: str) -> Optional[MemoryCell]:
        if cell.id == cell_id:
            return cell
        for child in cell.children:
            result = self._find(child, cell_id)
            if result:
                return result
        return None

    def total_memory(self) -> int:
        return sum(r.total_cells() for r in self._roots)

    def status(self) -> Dict[str, Any]:
        return {
            "plazas": len(self._roots),
            "total_cells": self.total_memory(),
            "total_recalls": self._recall_count,
        }
