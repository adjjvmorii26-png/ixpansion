from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class Mode(Enum):
    UNICAST = auto()
    MULTICAST = auto()
    FLOOD = auto()


@dataclass
class Channel:
    label: str
    mode: Mode = Mode.UNICAST
    participants: set[str] = field(default_factory=set)
    transcript: list[dict[str, Any]] = field(default_factory=list)

    def transmit(self, sender: str, body: dict[str, Any]) -> None:
        self.transcript.append({"src": sender, **body})

    @property
    def latest(self) -> dict[str, Any] | None:
        return self.transcript[-1] if self.transcript else None
