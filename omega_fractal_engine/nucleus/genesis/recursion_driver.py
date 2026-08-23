"""Recursive expansion engine — grows the engine's own structure."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class FractalNode:
    label: str
    depth: int
    children: list["FractalNode"] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)

    @property
    def size(self) -> int:
        return 1 + sum(c.size for c in self.children)


class RecursionDriver:
    def __init__(self, max_depth: int = 7, branching_factor: int = 2) -> None:
        self.max_depth = max_depth
        self.branching_factor = branching_factor
        self._root: FractalNode | None = None
        self._expansions = 0

    def seed(self, root_label: str, generator: Callable[[int, str], dict[str, Any]] | None = None) -> FractalNode:
        """Create root node and recursively expand."""
        self._root = FractalNode(label=root_label, depth=0)
        self._expand(self._root, generator)
        return self._root

    def _expand(self, node: FractalNode, generator: Callable | None) -> None:
        if node.depth >= self.max_depth:
            return
        for i in range(self.branching_factor):
            child_label = f"{node.label}.{i}"
            child = FractalNode(label=child_label, depth=node.depth + 1)
            if generator:
                child.data = generator(node.depth + 1, child_label)
            node.children.append(child)
            self._expansions += 1
            self._expand(child, generator)

    @property
    def tree_size(self) -> int:
        return self._root.size if self._root else 0

    @property
    def total_expansions(self) -> int:
        return self._expansions

    def prune(self, predicate: Callable[[FractalNode], bool]) -> int:
        """Recursively remove nodes matching predicate. Returns count removed."""
        if not self._root:
            return 0
        count = [0]

        def _prune(node: FractalNode) -> None:
            node.children = [c for c in node.children if not predicate(c)]
            count[0] += len(node.children)
            for child in node.children:
                _prune(child)

        _prune(self._root)
        return count[0]
