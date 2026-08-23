import copy
from typing import Any

from ..utils.logging import get_logger

logger = get_logger(__name__)


class StateManager:
    """Thread-safe-ish state store with snapshot/rollback."""

    def __init__(self) -> None:
        self._state: dict[str, Any] = {}
        self._snapshots: list[dict[str, Any]] = []

    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._state[key] = value
        logger.debug("state[%s] = %r", key, value)

    def delete(self, key: str) -> None:
        self._state.pop(key, None)

    def snapshot(self) -> None:
        self._snapshots.append(copy.deepcopy(self._state))

    def rollback(self) -> bool:
        if not self._snapshots:
            return False
        self._state = self._snapshots.pop()
        return True

    @property
    def state(self) -> dict[str, Any]:
        return copy.deepcopy(self._state)
