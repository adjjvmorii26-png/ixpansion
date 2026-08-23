"""Multi-layered event bus — events propagate through layers with filtering."""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable


LAYERS = ["physical", "social", "economic", "cultural", "meta"]


class EventMesh:
    """Events are published to a layer; subscribers on that layer and all higher layers receive them."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)  # layer -> [callbacks]
        self._event_log: list[dict[str, Any]] = []

    def subscribe(self, layer: str, callback: Callable[[dict[str, Any]], None]) -> None:
        if layer not in LAYERS:
            raise ValueError(f"Unknown layer: {layer}. Valid: {LAYERS}")
        self._subscribers[layer].append(callback)

    def publish(self, layer: str, event_type: str, payload: dict[str, Any]) -> int:
        """Publish event at a layer; propagates upward through the stack."""
        layer_idx = LAYERS.index(layer)
        delivered = 0

        entry = {"layer": layer, "type": event_type, "payload": payload}
        self._event_log.append(entry)

        for target_layer in LAYERS[layer_idx:]:
            for callback in self._subscribers.get(target_layer, []):
                try:
                    callback({"origin_layer": layer, "event": event_type, **payload})
                    delivered += 1
                except Exception:
                    pass

        # Cap log size
        if len(self._event_log) > 5000:
            self._event_log = self._event_log[-2500:]
        return delivered

    def query_events(self, layer: str | None = None,
                     event_type: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        results = self._event_log[-limit:]
        if layer:
            results = [e for e in results if e["layer"] == layer]
        if event_type:
            results = [e for e in results if e["type"] == event_type]
        return results

    @property
    def total_events(self) -> int:
        return len(self._event_log)
