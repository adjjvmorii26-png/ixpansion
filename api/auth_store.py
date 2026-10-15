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
    name = "abstract"

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
        return {"ok": True, "name": self.name}


class LocalJsonAuthStore(AuthStore):
    name = "local_json"

    def __init__(self, keys_file: Optional[Path] = None, usage_file: Optional[Path] = None):
        self.keys_file = keys_file or KEYS_FILE
        self.usage_file = usage_file or USAGE_FILE

    def ensure(self) -> None:
        self.keys_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            if not self.keys_file.exists():
                self.keys_file.write_text("{}")
            if not self.usage_file.exists():
                self.usage_file.write_text("{}")
        except OSError:
            pass

    def load_keys(self) -> Dict:
        self.ensure()
        try:
            return json.loads(self.keys_file.read_text())
        except Exception:
            return {}

    def save_keys(self, keys: Dict) -> None:
        self.ensure()
        self.keys_file.write_text(json.dumps(keys, indent=2))

    def load_usage(self) -> Dict:
        self.ensure()
        try:
            return json.loads(self.usage_file.read_text())
        except Exception:
            return {}

    def save_usage(self, usage: Dict) -> None:
        self.ensure()
        self.usage_file.write_text(json.dumps(usage, indent=2))

    def health(self) -> Dict:
        self.ensure()
        return {"ok": self.keys_file.parent.exists(), "name": self.name, "writable": True}


class MemoryAuthStore(AuthStore):
    name = "memory"

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
        return {"ok": True, "name": self.name, "writes": self.writes}


def register_auth_store(store: AuthStore) -> AuthStore:
    global _ACTIVE_STORE
    _ACTIVE_STORE = store
    return store


def get_auth_store() -> AuthStore:
    global _ACTIVE_STORE
    if _ACTIVE_STORE is not None:
        return _ACTIVE_STORE
    if SERVERLESS:
        raise RuntimeError(
            "auth persistence is not configured for serverless production; "
            "register a durable AuthStore via register_auth_store() or set "
            "IXPANSION_AUTH_STORE and provide an implemented adapter"
        )
    store = LocalJsonAuthStore()
    _ACTIVE_STORE = store
    return store


def assert_persistence_contract() -> None:
    if not SERVERLESS:
        return
    store = _ACTIVE_STORE
    if store is None or store.name in {"local_json", "abstract"}:
        raise RuntimeError(
            "auth persistence is not configured for serverless production; "
            "set IXPANSION_AUTH_STORE and register a durable AuthStore adapter"
        )
    health = store.health()
    if not health.get("ok"):
        raise RuntimeError("auth durable backend health check failed")
