from abc import ABC, abstractmethod
from typing import Any


class AgentInterface(ABC):
    """Contract that all agents must fulfill."""

    @abstractmethod
    def initialize(self, config: dict[str, Any]) -> None: ...

    @abstractmethod
    def perceive(self, observation: dict[str, Any]) -> None: ...

    @abstractmethod
    def decide(self) -> dict[str, Any]: ...

    @abstractmethod
    def act(self, action: dict[str, Any]) -> dict[str, Any]: ...
