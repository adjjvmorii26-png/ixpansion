"""Main pipeline orchestrator — builds and runs fractal pipelines."""
from __future__ import annotations

from typing import Any, Callable

from .fractal_steps.step_node import StepNode, StepResult
from .fractal_steps.step_graph import StepGraph


class PipelineEngine:
    """Builds a DAG of fractal steps and executes them in dependency order."""

    def __init__(self) -> None:
        self.graph = StepGraph()
        self._runs: list[dict[str, Any]] = []

    def add_step(self, step_id: str, handler: Callable | None = None,
                 parent_id: str | None = None) -> StepNode:
        """Add a step. If parent_id is given, nest inside it (fractal)."""
        node = StepNode(step_id, handler)
        if parent_id:
            parent = self.graph._nodes.get(parent_id)
            if not parent:
                raise KeyError(f"Parent step '{parent_id}' not registered")
            parent.add_child(node)
        else:
            self.graph.register(node)
        return node

    def execute(self, initial_context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = initial_context or {}
        raw_results = self.graph.execute(context)

        summary = {
            "steps_executed": len(raw_results),
            "total_fractal_steps": sum(r.total_steps for r in raw_results.values()),
            "all_success": all(r.success for r in raw_results.values()),
            "failures": [
                {"step": sid, "error": r.error}
                for sid, r in raw_results.items() if not r.success
            ],
            "outputs": {sid: r.output for sid, r in raw_results.items() if r.output is not None},
        }

        self._runs.append(summary)
        return summary

    @property
    def run_count(self) -> int:
        return len(self._runs)
