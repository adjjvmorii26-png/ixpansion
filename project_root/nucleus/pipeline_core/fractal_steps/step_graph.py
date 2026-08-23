"""Manages a directed graph of pipeline steps with dependency ordering."""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from .step_node import StepNode, StepResult


class StepGraph:
    def __init__(self) -> None:
        self._nodes: dict[str, StepNode] = {}
        self._edges: dict[str, list[str]] = defaultdict(list)  # from -> [to]

    def register(self, node: StepNode) -> None:
        self._nodes[node.step_id] = node

    def depends_on(self, step_id: str, prerequisite: str) -> None:
        """Declare that `step_id` must run after `prerequisite`."""
        self._edges[prerequisite].append(step_id)

    def topological_order(self) -> list[str]:
        """Return execution order respecting dependencies."""
        in_degree = defaultdict(int)
        all_nodes = set(self._nodes.keys())
        for prereq, dependents in self._edges.items():
            for dep in dependents:
                in_degree[dep] += 1

        queue = deque(sorted(all_nodes - set(in_degree)))
        order = []
        while queue:
            current = queue.popleft()
            order.append(current)
            for dep in self._edges[current]:
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)
        return order

    def execute(self, context: dict[str, Any]) -> dict[str, StepResult]:
        """Execute all steps in topological order."""
        results = {}
        for step_id in self.topological_order():
            node = self._nodes[step_id]
            results[step_id] = node.execute(context)
        return results

    @property
    def total_steps(self) -> int:
        return sum(n.size for n in self._nodes.values())
