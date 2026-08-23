"""Triggers high-level system behaviors programmatically."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class RitualResult:
    ritual_name: str
    success: bool
    duration_ticks: int
    participants: list[str]
    effects: dict[str, Any] = field(default_factory=dict)


class Invocation:
    def __init__(self) -> None:
        self._rituals: dict[str, list[Callable[[dict[str, Any]], RitualResult]]] = defaultdict(list)
        self._history: list[RitualResult] = []

    def register(self, name: str, handler: Callable[[dict[str, Any]], RitualResult]) -> None:
        self._rituals[name].append(handler)

    def invoke(self, name: str, context: dict[str, Any]) -> list[RitualResult]:
        """Invoke all handlers registered for a ritual."""
        results = []
        for handler in self._rituals.get(name, []):
            try:
                result = handler(context)
                results.append(result)
                self._history.append(result)
            except Exception as e:
                results.append(RitualResult(ritual_name=name, success=False,
                                            duration_ticks=0,
                                            participants=[],
                                            effects={"error": str(e)}))
        return results

    @property
    def known_rituals(self) -> list[str]:
        return [name for name, handlers in self._rituals.items() if handlers]

    @property
    def recent(self) -> list[dict[str, Any]]:
        return [
            {"name": r.ritual_name, "ok": r.success, "ticks": r.duration_ticks}
            for r in self._history[-10:]
        ]
