from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class ChannelType(Enum):
    DIRECT = auto()
    BROADCAST = auto()
    MULTICAST = auto()


@dataclass
class Channel:
    name: str
    type: ChannelType = ChannelType.DIRECT
    members: set[str] = field(default_factory=set)
    history: list[dict[str, Any]] = field(default_factory=list)

    def send(self, sender: str, message: dict[str, Any]) -> None:
        entry = {"from": sender, **message}
        self.history.append(entry)

    @property
    def last_message(self) -> dict[str, Any] | None:
        return self.history[-1] if self.history else None
