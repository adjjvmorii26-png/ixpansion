from abc import ABC, abstractmethod
from typing import Any


class ProtocolPort(ABC):
    """Contract for wire-format codecs."""

    @abstractmethod
    def frame(self, payload: dict[str, Any]) -> bytes: ...

    @abstractmethod
    def unframe(self, raw: bytes) -> dict[str, Any]: ...
