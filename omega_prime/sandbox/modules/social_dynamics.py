from collections import defaultdict
from typing import Any


class SocialDynamics:
    """Relationship graph with affinity propagation."""

    def __init__(self) -> None:
        self._matrix: dict[str, dict[str, float]] = defaultdict(dict)

    def bond(self, a: str, b: str, delta: float = 0.05) -> None:
        for pair in [(a, b), (b, a)]:
            current = self._matrix[pair[0]].get(pair[1], 0.0)
            self._matrix[pair[0]][pair[1]] = max(-1.0, min(1.0, current + delta))

    def trust(self, a: str, b: str) -> float:
        return self._matrix.get(a, {}).get(b, 0.0)

    def faction_of(self, agent_id: str, threshold: float = 0.3) -> set[str]:
        return {peer for peer, w in self._matrix.get(agent_id, {}).items() if w >= threshold}
