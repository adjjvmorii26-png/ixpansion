# Wave 405: Storage Vault Organ
# Provides vault behavior simulation for module persistence

"""Storage Vault - Organ for persistent module storage with integrity verification."""

import json
import hashlib
import time
from typing import Dict, Any, Optional, List


class StorageVault:
    """Vault for storing module data with protocol compliance."""
    
    def __init__(self, vault_id: str = None, capacity: int = 1000):
        self.vault_id = vault_id or f"vault_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:12]}"
        self.capacity = capacity
        self.storage: Dict[str, Any] = {}
        self.current_items = 0
        self.access_log: List[Dict] = []
        self.created_at = time.time()
        self._locked = False
    
    def store(self, key: str, value: Any) -> bool:
        if self._locked:
            return False
        if len(self.storage) >= self.capacity:
            self._evict_oldest()
        entry = {"value": value, "stored_at": time.time(), "key": key, "access_count": 0}
        self.storage[key] = entry
        self.current_items = len(self.storage)
        self._log("store", key)
        return True
    
    def retrieve(self, key: str) -> Optional[Any]:
        if key not in self.storage:
            return None
        entry = self.storage[key]
        entry["access_count"] += 1
        self._log("retrieve", key)
        return entry["value"]
    
    def _evict_oldest(self):
        if not self.storage:
            return
        oldest = min(self.storage.keys(), key=lambda k: self.storage[k].get("stored_at", 0))
        del self.storage[oldest]
        self.current_items = len(self.storage)
    
    def lock(self): self._locked = True
    def unlock(self): self._locked = False
    
    def status(self) -> Dict[str, Any]:
        return {
            "vault_id": self.vault_id,
            "capacity": self.capacity,
            "current_items": self.current_items,
            "locked": self._locked,
            "created_at": self.created_at,
            "total_accesses": len(self.access_log),
        }
    
    def _log(self, action: str, key: str):
        self.access_log.append({"action": action, "key": key, "timestamp": time.time()})


# Global vault instance
_vault = None

def get_vault(capacity: int = 1000) -> StorageVault:
    global _vault
    if _vault is None:
        _vault = StorageVault(capacity=capacity)
    return _vault


def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    """Vercel-compatible handler."""
    action = payload.get("action", "status")
    vault = get_vault()
    
    if action == "store":
        key = payload.get("key", "")
        value = payload.get("value", {})
        success = vault.store(key, value)
        return {"status": "stored" if success else "failed", "vault_id": vault.vault_id}
    
    elif action == "retrieve":
        key = payload.get("key", "")
        value = vault.retrieve(key)
        return {"status": "retrieved" if value is not None else "not_found", "value": value}
    
    elif action == "status":
        return {"status": "ok", "vault": vault.status()}
    
    elif action == "lock":
        vault.lock()
        return {"status": "locked", "vault_id": vault.vault_id}
    
    elif action == "unlock":
        vault.unlock()
        return {"status": "unlocked", "vault_id": vault.vault_id}
    
    return {"status": "error", "message": f"Unknown action: {action}"}
