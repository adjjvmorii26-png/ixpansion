from __future__ import annotations
from typing import Any

from core.state_graph import StateGraph
from expansion.models.mutation import Mutation


class MutationApplier:
    def apply(self, graph: StateGraph, mutation: Mutation) -> bool:
        node = graph.nodes.get(mutation.target)
        if node is None:
            return False
        current = node.state.get(mutation.field)
        if mutation.operation == "set":
            node.state[mutation.field] = mutation.value
        elif mutation.operation == "add":
            node.state[mutation.field] = (current or 0) + mutation.value
        elif mutation.operation == "multiply":
            node.state[mutation.field] = (current or 0) * mutation.value
        else:
            values = list(current or [])
            values.append(mutation.value)
            node.state[mutation.field] = values
        return True
