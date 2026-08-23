from __future__ import annotations

from core.state_graph import StateGraph
from expansion.models.mutation import Mutation
from expansion.models.rule import Rule
from expansion.mutation_applier import MutationApplier


class RuleEngine:
    def __init__(self) -> None:
        self.rules: list[Rule] = []
        self.applier = MutationApplier()

    def add(self, rule: Rule) -> None:
        self.rules.append(rule)

    def evaluate(self, graph: StateGraph) -> list[str]:
        applied: list[str] = []
        for rule in self.rules:
            for node in graph.nodes.values():
                if rule.path not in node.state:
                    continue
                actual = float(node.state[rule.path])
                matches = {
                    ">": actual > rule.value,
                    "<": actual < rule.value,
                    ">=": actual >= rule.value,
                    "<=": actual <= rule.value,
                    "==": actual == rule.value,
                }[rule.operator]
                if matches and rule.mutation_id and self.applier.apply(
                    graph,
                    Mutation(
                        target=node.id, field=rule.path, operation="multiply", value=0.9
                    ),
                ):
                    applied.append(rule.id)
                    break
        return applied
