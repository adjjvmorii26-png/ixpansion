from abc import ABC, abstractmethod
from typing import Any


class ProtocolInterface(ABC):
    """Contract for communication protocols."""

    @abstractmethod
    def encode(self, payload: dict[str, Any]) -> bytes: ...

    @abstractmethod
    def decode(self, raw: bytes) -> dict[str, Any]: ...
