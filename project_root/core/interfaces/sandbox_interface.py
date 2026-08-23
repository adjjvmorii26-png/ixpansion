from abc import ABC, abstractmethod
from typing import Any


class SandboxInterface(ABC):
    """Contract for sandbox environments."""

    @abstractmethod
    def setup(self, config: dict[str, Any]) -> None: ...

    @abstractmethod
    def step(self, actions: list[dict[str, Any]]) -> dict[str, Any]: ...

    @abstractmethod
    def reset(self) -> dict[str, Any]: ...

    @abstractmethod
    def teardown(self) -> None: ...
