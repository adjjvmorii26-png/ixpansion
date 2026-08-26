"""Wave 128 — Dimensional Thread.

Threads that connect parallel dimensions of the system — each thread
carries information between reality layers, allowing modules in
different dimensions to communicate and share state.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class DimensionalThread:
    """A thread connecting two dimensions."""

    def __init__(self, name: str, dim_a: str, dim_b: str):
        self.name = name
        self.dim_a = dim_a
        self.dim_b = dim_b
        self.created = time.time()
        self.messages: List[Dict[str, Any]] = []
        self.strength = 1.0
        self.id = hashlib.sha256(f"thread:{name}".encode()).hexdigest()[:10]

    def send(self, message: str, direction: str = "a_to_b") -> Dict[str, Any]:
        self.messages.append({"message": message, "direction": direction,
                               "timestamp": time.time()})
        self.strength = min(1.0, self.strength + 0.02)
        return {"sent": True, "direction": direction, "strength": round(self.strength, 4)}

    def weaken(self, amount: float = 0.1) -> float:
        self.strength = max(0.0, self.strength - amount)
        return self.strength

    def is_active(self) -> bool:
        return self.strength > 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "dim_a": self.dim_a,
                "dim_b": self.dim_b, "strength": round(self.strength, 4),
                "messages": len(self.messages), "active": self.is_active()}


class DimensionalThreadingNetwork:
    """Network of threads connecting parallel dimensions."""

    def __init__(self):
        self._threads: Dict[str, DimensionalThread] = {}
        self._dimensions: set = set()
        self._total_messages = 0

    def create_thread(self, name: str, dim_a: str, dim_b: str) -> DimensionalThread:
        thread = DimensionalThread(name, dim_a, dim_b)
        self._threads[thread.id] = thread
        self._dimensions.add(dim_a)
        self._dimensions.add(dim_b)
        return thread

    def send(self, thread_id: str, message: str, direction: str = "a_to_b") -> Dict[str, Any]:
        thread = self._threads.get(thread_id)
        if not thread:
            return {"error": "thread not found"}
        result = thread.send(message, direction)
        self._total_messages += 1
        return result

    def get_threads(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self._threads.values()]

    def active_threads(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self._threads.values() if t.is_active()]

    def status(self) -> Dict[str, Any]:
        return {"total_threads": len(self._threads), "dimensions": len(self._dimensions),
                "total_messages": self._total_messages,
                "active": sum(1 for t in self._threads.values() if t.is_active())}
