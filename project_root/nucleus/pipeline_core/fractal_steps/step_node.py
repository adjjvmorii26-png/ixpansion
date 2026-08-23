"""A single step in a fractal pipeline. Steps can recursively nest."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class StepResult:
    step_id: str
    success: bool
    output: Any = None
    error: str | None = None
    children_results: list["StepResult"] = field(default_factory=list)

    @property
    def total_steps(self) -> int:
        return 1 + sum(c.total_steps for c in self.children_results)


class StepNode:
    """A pipeline step that can contain child steps (fractal nesting)."""

    def __init__(self, step_id: str, handler: Callable[[dict[str, Any]], Any] | None = None,
                 max_depth: int = 5) -> None:
        self.step_id = step_id
        self.handler = handler
        self.max_depth = max_depth
        self.children: list[StepNode] = []
        self._depth = 0

    def add_child(self, child: "StepNode") -> "StepNode":
        child._depth = self._depth + 1
        child.max_depth = self.max_depth
        if child._depth > self.max_depth:
            raise RecursionError(f"Max depth {self.max_depth} exceeded at '{child.step_id}'")
        self.children.append(child)
        return child

    def execute(self, context: dict[str, Any]) -> StepResult:
        """Execute this step and all children recursively."""
        result = StepResult(step_id=self.step_id, success=True)

        if self.handler:
            try:
                result.output = self.handler(context)
            except Exception as exc:
                result.success = False
                result.error = str(exc)
                return result

        child_context = {"parent_output": result.output} if result.output is not None else context
        for child in self.children:
            exec_ctx = child_context if isinstance(child_context, dict) else context
            child_result = child.execute(exec_ctx)
            result.children_results.append(child_result)
            if not child_result.success:
                result.success = False
                result.error = f"child '{child.step_id}' failed: {child_result.error}"
                break

        return result

    @property
    def size(self) -> int:
        return 1 + sum(c.size for c in self.children)
