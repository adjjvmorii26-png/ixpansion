"""Wave 140 — State Lock.

A process-wide advisory lock for exclusive access to a namespace.
Prevents concurrent writes from clobbering runtime state. Uses an
in-process re-entrant lock keyed by namespace (coarse but safe within
a single worker, which is the Vercel model).
"""
from __future__ import annotations

import time
import threading
from typing import Any, Dict


class StateLock:
    """Per-namespace advisory locks."""

    def __init__(self):
        self._locks: Dict[str, threading.RLock] = {}
        self._held: Dict[str, int] = {}

    def _lock_for(self, namespace: str) -> threading.RLock:
        if namespace not in self._locks:
            self._locks[namespace] = threading.RLock()
        return self._locks[namespace]

    def acquire(self, namespace: str, blocking: bool = True) -> bool:
        lock = self._lock_for(namespace)
        acquired = lock.acquire(blocking=blocking)
        if acquired:
            self._held[namespace] = self._held.get(namespace, 0) + 1
        return acquired

    def release(self, namespace: str) -> bool:
        """Release one hold. Fully frees when all holds are released."""
        lock = self._locks.get(namespace)
        if lock is None:
            return False
        try:
            lock.release()
        except RuntimeError:
            return False
        count = self._held.get(namespace, 0)
        if count <= 1:
            self._held.pop(namespace, None)
        else:
            self._held[namespace] = count - 1
        return True

    def context(self, namespace: str):
        """Small context manager for with-statement usage."""
        class _Ctx:
            def __init__(self, owner, ns):
                self.owner = owner
                self.ns = ns
            def __enter__(self):
                self.owner.acquire(self.ns)
            def __exit__(self, *exc):
                self.owner.release(self.ns)
                return False
        return _Ctx(self, namespace)

    def status(self) -> Dict[str, Any]:
        return {"namespaces": len(self._locks), "active": len(self._held)}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    lock = StateLock()
    return {"status": "active", "module": "state_lock", **lock.status()}
