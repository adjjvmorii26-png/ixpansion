import copy
import hashlib
import json
from typing import Any


class StateCore:
    """Immutable-by-default global state atom with content-addressed snapshots."""

    def __init__(self, initial: dict[str, Any] | None = None) -> None:
        self._state: dict[str, Any] = initial or {}
        self._history: list[tuple[str, dict[str, Any]]] = []

    def get(self, path: str, default: Any = None) -> Any:
        keys = path.split(".")
        node = self._state
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return copy.deepcopy(node)

    def set(self, path: str, value: Any) -> None:
        keys = path.split(".")
        node = self._state
        for key in keys[:-1]:
            node = node.setdefault(key, {})
        old = copy.deepcopy(node.get(keys[-1]))
        node[keys[-1]] = copy.deepcopy(value)
        digest = self._digest()
        self._history.append((digest, {keys[-1]: {"from": old, "to": value}}))

    def delete(self, path: str) -> bool:
        keys = path.split(".")
        node = self._state
        for key in keys[:-1]:
            if not isinstance(node, dict) or key not in node:
                return False
            node = node[key]
        return node.pop(keys[-1], None) is not None

    def snapshot(self) -> str:
        frozen = json.dumps(self._state, sort_keys=True, default=str)
        return hashlib.sha256(frozen.encode()).hexdigest()

    def _digest(self) -> str:
        return hashlib.sha256(json.dumps(self._state, sort_keys=True, default=str).encode()).hexdigest()[:16]

    @property
    def raw(self) -> dict[str, Any]:
        return copy.deepcopy(self._state)
