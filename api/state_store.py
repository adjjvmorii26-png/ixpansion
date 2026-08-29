"""Wave 140 — State Store.

A shared atomic JSON store for durable runtime state. Every write is
buffered in memory, flushed atomically to `.runtime/<namespace>.json`
(temp-file + rename), and reloaded lazily on read — so state survives
Vercel cold starts without corrupting under concurrent access.
"""
from __future__ import annotations

import json
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"

_lock = threading.RLock()
_cache: Dict[str, Dict[str, Any]] = {}


def _path(namespace: str) -> Path:
    return RUNTIME / f"{namespace}.json"


def read(namespace: str, default: Any = None) -> Any:
    """Read a stored namespace (with process cache)."""
    with _lock:
        if namespace in _cache:
            return _cache[namespace]
        path = _path(namespace)
        try:
            if path.exists():
                data = json.loads(path.read_text())
                _cache[namespace] = data
                return data
        except (OSError, json.JSONDecodeError):
            pass
        return default


def write(namespace: str, data: Any) -> bool:
    """Atomically write a namespace via temp-file + rename."""
    with _lock:
        try:
            RUNTIME.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=str(RUNTIME), suffix=".tmp")
            try:
                with os.fdopen(fd, "w") as f:
                    json.dump(data, f)
            except Exception:
                os.unlink(tmp)
                raise
            os.replace(tmp, _path(namespace))
            _cache[namespace] = data
            return True
        except OSError:
            return False


def append(namespace: str, entry: Any) -> bool:
    data = read(namespace, [])
    if not isinstance(data, list):
        data = []
    data.append(entry)
    return write(namespace, data)


def delete(namespace: str) -> bool:
    with _lock:
        _cache.pop(namespace, None)
        try:
            path = _path(namespace)
            if path.exists():
                path.unlink()
                return True
        except OSError:
            pass
        return False


def flush_cache() -> None:
    with _lock:
        _cache.clear()


class StateStore:
    """Object-oriented facade over the shared atomic store."""

    def __init__(self, namespace: str):
        self.namespace = namespace

    def get(self, default: Any = None) -> Any:
        return read(self.namespace, default)

    def set(self, data: Any) -> bool:
        return write(self.namespace, data)

    def update(self, patch: Dict[str, Any]) -> Dict[str, Any]:
        data = self.get({})
        if not isinstance(data, dict):
            data = {}
        data.update(patch)
        self.set(data)
        return data

    def status(self) -> Dict[str, Any]:
        path = _path(self.namespace)
        return {"namespace": self.namespace, "exists": path.exists(),
                "size_bytes": path.stat().st_size if path.exists() else 0}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    store = StateStore(payload.get("namespace", "state_store"))
    return {"status": "active", "module": "state_store", **store.status()}
