# Vault Simulator Module
# Simulates vault behavior for storage protocols in the ixpansion organism

"""Vault Simulator for ixpansion organism storage.

Handles vault creation, access, mutation, and lifecycle management
for the organism's storage layer.
"""

import json
import hashlib
import time
from typing import Dict, Any, Optional, List


class VaultSimulator:
    """Simulates vault behavior for the ixpansion organism storage layer."""
    
    def __init__(self, vault_id: str = None, capacity: int = 1000):
        self.vault_id = vault_id or self._generate_vault_id()
        self.capacity = capacity
        self.storage: Dict[str, Any] = {}
        self.current_items: int = 0
        self.access_log: List[Dict] = []
        self.created_at = time.time()
        self._locked = False
    
    def _generate_vault_id(self) -> str:
        """Generate a unique vault identifier."""
        return f"vault_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:12]}"
    
    def store(self, key: str, value: Any) -> bool:
        """Store a value in the vault with optional TTL."""
        if self._locked:
            return False
        
        # Check capacity
        if len(self.storage) >= self.capacity and self.current_items >= self.capacity:
            self._evict_oldest()
        
        entry = {
            "value": value,
            "stored_at": time.time(),
            "key": key,
            "access_count": 0,
        }
        
        self.storage[key] = entry
        self.current_items = len(self.storage)
        self._log_access("store", key)
        return True
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value from the vault."""
        if key not in self.storage:
            return None
        
        entry = self.storage[key]
        entry["access_count"] += 1
        self._log_access("retrieve", key)
        
        # Update current_items tracking
        self.current_items = len(self.storage)
        
        return entry["value"]
    
    def delete(self, key: str) -> bool:
        """Delete a key from the vault."""
        if key in self.storage:
            del self.storage[key]
            self.current_items = len(self.storage)
            self._log_access("delete", key)
            return True
        return False
    
    def _evict_oldest(self) -> None:
        """Evict the oldest accessed item when at capacity."""
        if not self.storage:
            return
        
        oldest_key = min(
            self.storage.keys(),
            key=lambda k: self.storage[k].get("stored_at", 0)
        )
        del self.storage[oldest_key]
        self.current_items = len(self.storage)
    
    def lock(self) -> None:
        """Lock the vault to prevent further modifications."""
        self._locked = True
    
    def unlock(self) -> None:
        """Unlock the vault."""
        self._locked = False
    
    def status(self) -> Dict[str, Any]:
        """Return vault status information."""
        return {
            "vault_id": self.vault_id,
            "capacity": self.capacity,
            "current_items": self.current_items,
            "locked": self._locked,
            "created_at": self.created_at,
        }
    
    def _log_access(self, action: str, key: str) -> None:
        """Log an access action to the vault's access log."""
        self.access_log.append({
            "action": action,
            "key": key,
            "timestamp": time.time(),
            "vault_id": self.vault_id,
        })


# Factory function for easy instantiation
def create_vault(vault_id: str = None, capacity: int = 1000) -> VaultSimulator:
    """Create a new vault instance."""
    return VaultSimulator(vault_id=vault_id, capacity=capacity)
