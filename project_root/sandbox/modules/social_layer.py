from collections import defaultdict
from typing import Any


class SocialLayer:
    """Tracks relationships between agents as a weighted graph."""

    def __init__(self) -> None:
        self._relations: dict[str, dict[str, float]] = defaultdict(dict)

    def interact(self, agent_a: str, agent_b: str, delta: float = 0.1) -> None:
        current = self._relations[agent_a].get(agent_b, 0.0)
        new_val = max(-1.0, min(1.0, current + delta))
        self._relations[agent_a][agent_b] = new_val
        self._relations[agent_b][agent_a] = new_val

    def affinity(self, agent_a: str, agent_b: str) -> float:
        return self._relations.get(agent_a, {}).get(agent_b, 0.0)

    def allies_of(self, agent_id: str, threshold: float = 0.5) -> list[str]:
        return [
            other for other, weight in self._relations.get(agent_id, {}).items()
            if weight >= threshold
        ]
