"""Auth persistence adapters — durable store contract for serverless."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional

ROOT = Path(__file__).resolve().parents[1]
USAGE_FILE = ROOT / ".runtime" / "usage.json"
KEYS_FILE = ROOT / ".runtime" / "api_keys.json"

PERSISTENCE_BACKEND = os.environ.get("IXPANSION_AUTH_STORE", "").strip().lower()
SERVERLESS = bool(os.environ.get("VERCEL") or os.environ.get("NOW_REGION"))
_ACTIVE_STORE = None


class AuthStore:
    """Storage interface. Implementations must opt into durability explicitly."""

    name = "abstract"
    durable = False

    def ensure(self) -> None:
        raise NotImplementedError

    def load_keys(self) -> Dict:
        raise NotImplementedError

    def save_keys(self, keys: Dict) -> None:
        raise NotImplementedError

    def load_usage(self) -> Dict:
        raise NotImplementedError

    def save_usage(self, usage: Dict) -> None:
        raise NotImplementedError

    def health(self) -> Dict:
        return {"ok": False, "name": self.name, "durable": self.durable}


class LocalJsonAuthStore(AuthStore):
    """Local development/test store only; not durable across serverless instances."""

    name = "local_json"
    durable = False

    def __init__(self, keys_file: Optional[Path] = None, usage_file: Optional[Path] = None):
        self.keys_file = keys_file or KEYS_FILE
        self.usage_file = usage_file or USAGE_FILE

    def ensure(self) -> None:
        self.keys_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.keys_file.exists():
            self.keys_file.write_text("{}")
        if not self.usage_file.exists():
            self.usage_file.write_text("{}")

    def load_keys(self) -> Dict:
        self.ensure()
        return json.loads(self.keys_file.read_text())

    def save_keys(self, keys: Dict) -> None:
        self.ensure()
        self.keys_file.write_text(json.dumps(keys, indent=2))

    def load_usage(self) -> Dict:
        self.ensure()
        return json.loads(self.usage_file.read_text())

    def save_usage(self, usage: Dict) -> None:
        self.ensure()
        self.usage_file.write_text(json.dumps(usage, indent=2))

    def health(self) -> Dict:
        self.ensure()
        return {
            "ok": self.keys_file.parent.exists(),
            "name": self.name,
            "writable": os.access(self.keys_file.parent, os.W_OK),
            "durable": False,
        }


class MemoryAuthStore(AuthStore):
    """In-memory test double; never valid for production persistence."""

    name = "memory"
    durable = False

    def __init__(self):
        self._keys: Dict = {}
        self._usage: Dict = {}
        self.writes = 0

    def ensure(self) -> None:
        return None

    def load_keys(self) -> Dict:
        return dict(self._keys)

    def save_keys(self, keys: Dict) -> None:
        self._keys = dict(keys)
        self.writes += 1

    def load_usage(self) -> Dict:
        return dict(self._usage)

    def save_usage(self, usage: Dict) -> None:
        self._usage = dict(usage)
        self.writes += 1

    def health(self) -> Dict:
        return {"ok": True, "name": self.name, "writes": self.writes, "durable": False}


def register_auth_store(store: AuthStore) -> AuthStore:
    """Register an implementation; serverless contract validates its durability."""
    global _ACTIVE_STORE
    _ACTIVE_STORE = store
    return store


def get_auth_store() -> AuthStore:
    global _ACTIVE_STORE
    if SERVERLESS:
        assert_persistence_contract()
        return _ACTIVE_STORE
    if _ACTIVE_STORE is not None:
        return _ACTIVE_STORE
    store = LocalJsonAuthStore()
    _ACTIVE_STORE = store
    return store


def assert_persistence_contract() -> None:
    if not SERVERLESS:
        return
    store = _ACTIVE_STORE
    if store is None or not isinstance(store, AuthStore) or store.durable is not True:
        raise RuntimeError(
            "auth persistence requires a registered durable AuthStore adapter; "
            "IXPANSION_AUTH_STORE alone does not establish durability"
        )
    health = store.health()
    if health.get("ok") is not True or health.get("durable") is not True:
        raise RuntimeError("auth durable backend health check failed")
