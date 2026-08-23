"""Base agent class for the project_root engine."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..utils.id_gen import generate_id
from ..utils.entropy import EntropySource


@dataclass
class AgentState:
    agent_id: str
    species: str
    energy: float = 100.0
    position: tuple[float, float] = (0.0, 0.0)
    alive: bool = True
    traits: dict[str, float] = field(default_factory=dict)
    memory: list[dict[str, Any]] = field(default_factory=list)

    @property
    def is_viable(self) -> bool:
        return self.alive and self.energy > 0


class BaseAgent(ABC):
    def __init__(self, species: str, entropy: EntropySource | None = None) -> None:
        self.state = AgentState(
            agent_id=generate_id("agent"),
            species=species,
            traits={
                "aggression": round((entropy or EntropySource()).float(0, 1), 3),
                "curiosity": round((entropy or EntropySource()).float(0, 1), 3),
                "cooperation": round((entropy or EntropySource()).float(0, 1), 3),
            },
        )
        self._entropy = entropy or EntropySource()

    @abstractmethod
    def decide(self, observation: dict[str, Any]) -> dict[str, Any]:
        """Return an action dict."""

    def act(self, action: dict[str, Any]) -> dict[str, Any]:
        self.state.memory.append({"tick": len(self.state.memory), "action": action})
        return {"agent": self.state.agent_id, **action}

    def drain_energy(self, amount: float) -> None:
        self.state.energy = max(0.0, self.state.energy - amount)
        if self.state.energy <= 0:
            self.state.alive = False
