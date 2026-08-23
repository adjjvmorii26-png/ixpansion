from abc import ABC, abstractmethod
from typing import Any


class AgentPort(ABC):
    """Contract for all autonomous entities in the system."""

    @abstractmethod
    def awaken(self, config: dict[str, Any]) -> None: ...

    @abstractmethod
    def observe(self, stimulus: dict[str, Any]) -> None: ...

    @abstractmethod
    def deliberate(self) -> dict[str, Any]: ...

    @abstractmethod
    def execute(self, intent: dict[str, Any]) -> dict[str, Any]: ...
