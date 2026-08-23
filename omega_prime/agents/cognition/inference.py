from typing import Any


class InferenceEngine:
    """Forward-chaining rule evaluator."""

    def __init__(self) -> None:
        self._rules: list[tuple[Any, str]] = []

    def add_rule(self, predicate: Any, conclusion: str) -> None:
        self._rules.append((predicate, conclusion))

    def fire(self, facts: dict[str, Any]) -> list[str]:
        triggered = [c for p, c in self._rules if p(facts)]
        return triggered
