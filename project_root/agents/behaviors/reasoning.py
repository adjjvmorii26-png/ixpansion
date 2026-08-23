from typing import Any


class Reasoner:
    """Rule-chain reasoner: evaluates conditions and returns conclusions."""

    def __init__(self) -> None:
        self._rules: list[tuple[callable, str]] = []

    def add_rule(self, condition: callable, conclusion: str) -> None:
        self._rules.append((condition, conclusion))

    def evaluate(self, context: dict[str, Any]) -> list[str]:
        return [conclusion for cond, conclusion in self._rules if cond(context)]
