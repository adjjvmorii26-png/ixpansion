from __future__ import annotations

from core.state_graph import StateGraph
from expansion.models.mutation import Mutation
from expansion.models.rule import Rule
from expansion.mutation_applier import MutationApplier


class RuleEngine:
    def __init__(self) -> None:
        self.rules: list[Rule] = []
        self.mutations: dict[str, Mutation] = {}
        self.applier = MutationApplier()

    def add(self, rule: Rule) -> None:
        self.rules.append(rule)

    def register_mutation(self, mutation_id: str, mutation: Mutation) -> None:
        self.mutations[mutation_id] = mutation

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
                if not matches or not rule.mutation_id:
                    continue
                fallback = Mutation(node.id, rule.path, "multiply", 0.9)
                mutation = self.mutations.get(rule.mutation_id, fallback)
                if self.applier.apply(graph, mutation):
                    applied.append(rule.id)
                    break
        return applied
