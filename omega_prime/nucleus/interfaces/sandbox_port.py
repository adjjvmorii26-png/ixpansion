from abc import ABC, abstractmethod
from typing import Any


class SandboxPort(ABC):
    """Contract for realm implementations."""

    @abstractmethod
    def materialize(self, config: dict[str, Any]) -> None: ...

    @abstractmethod
    def advance(self, intents: list[dict[str, Any]]) -> dict[str, Any]: ...

    @abstractmethod
    def dissolve(self) -> None: ...
