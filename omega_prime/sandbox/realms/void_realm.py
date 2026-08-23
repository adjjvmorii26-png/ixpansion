from typing import Any

from ...nucleus.interfaces.sandbox_port import SandboxPort


class VoidRealm(SandboxPort):
    """Empty space — agents exist but have no spatial constraints."""

    def __init__(self) -> None:
        self._entities: dict[str, dict[str, Any]] = {}
        self._epoch = 0

    def materialize(self, config: dict[str, Any]) -> None:
        self._entities = config.get("entities", {})
        self._epoch = 0

    def advance(self, intents: list[dict[str, Any]]) -> dict[str, Any]:
        self._epoch += 1
        return {"epoch": self._epoch, "processed": len(intents)}

    @property
    def observation(self) -> dict[str, Any]:
        return {"realm": "void", "entities": list(self._entities.keys())}

    def dissolve(self) -> None:
        self._entities.clear()
