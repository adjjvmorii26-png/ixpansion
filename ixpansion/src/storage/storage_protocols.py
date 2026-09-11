# Storage Protocols Module
# Defines storage protocols and vault behavior for ixpansion organism

"""Storage Protocols for ixpansion organism.

Defines the interface and protocols that govern how storage
interacts with the organism's architecture.
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional, List
from .vault_simulator import VaultSimulator, create_vault


class StorageProtocols:
    """Storage protocols governing vault behavior and interactions."""
    
    def __init__(self, vault: VaultSimulator = None):
        self.vault = vault or create_vault()
        self.protocol_version = "2.3.2"
        self.active_contracts: Dict[str, Any] = {}
    
    def initialize_vault(self, capacity: int = 1000, vault_id: str = None) -> VaultSimulator:
        """Initialize or reset the vault with specified capacity."""
        self.vault = create_vault(vault_id=vault_id, capacity=capacity)
        return self.vault
    
    def store_module_data(self, module_id: str, data: Dict[str, Any]) -> bool:
        """Store module data in the vault with protocol-compliant formatting."""
        # Create protocol-wrapped data
        protocol_data = {
            "@type": "module_data",
            "module_id": module_id,
            "protocol_version": self.protocol_version,
            "timestamp": time.time(),
            "payload": data,
        }
        
        # Hash the payload for integrity
        payload_hash = hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()[:16]
        protocol_data["payload_hash"] = payload_hash
        
        # Store in vault
        key = f"module:{module_id}"
        return self.vault.store(key, protocol_data)
    
    def retrieve_module_data(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve module data from the vault."""
        key = f"module:{module_id}"
        raw_data = self.vault.retrieve(key)
        
        if raw_data is None:
            return None
        
        # Validate protocol structure
        if raw_data.get("@type") != "module_data":
            return None
        
        # Verify hash integrity
        stored_hash = raw_data.get("payload_hash")
        if stored_hash:
            payload = raw_data.get("payload", {})
            expected_hash = hashlib.sha256(
                json.dumps(payload, sort_keys=True).encode()
            ).hexdigest()[:16]
            if stored_hash != expected_hash:
                # Hash mismatch - return partial data with warning
                raw_data["_hash_warning"] = "integrity_check_failed"
        
        return raw_data.get("payload")
    
    def sync_vault_state(self, other_vault: VaultSimulator) -> Dict[str, Any]:
        """Synchronize state between two vault instances."""
        sync_report = {
            "synced_keys": [],
            "conflicts": [],
            "missing_in_other": [],
            "errors": [],
        }
        
        # Get current keys from both vaults
        self_keys = set(self.vault.storage.keys())
        other_keys = set(other_vault.storage.keys())
        
        # Keys to sync (in self but not in other)
        to_sync = self_keys - other_keys
        
        for key in to_sync:
            value = self.vault.retrieve(key)
            if value is not None:
                try:
                    success = other_vault.store(key, value)
                    if success:
                        sync_report["synced_keys"].append(key)
                    else:
                        sync_report["errors"].append(f"Failed to sync {key}")
                except Exception as e:
                    sync_report["errors"].append(f"Error syncing {key}: {str(e)}")
        
        # Check for conflicts (same key, different values)
        common_keys = self_keys & other_keys
        for key in common_keys:
            self_val = self.vault.retrieve(key)
            other_val = other_vault.retrieve(key)
            
            if self_val != other_val:
                sync_report["conflicts"].append({
                    "key": key,
                    "self_type": type(self_val).__name__,
                    "other_type": type(other_val).__name__,
                })
        
        # Keys missing in self
        missing_in_self = other_keys - self_keys
        sync_report["missing_in_other"] = list(missing_in_self)
        
        return sync_report
    
    def generate_vault_report(self) -> Dict[str, Any]:
        """Generate a comprehensive vault status report."""
        vault_status = self.vault.status()
        
        return {
            "protocol_version": self.protocol_version,
            "vault_id": vault_status["vault_id"],
            "capacity": vault_status["capacity"],
            "current_items": vault_status["current_items"],
            "locked": vault_status["locked"],
            "total_accesses": len(self.vault.access_log),
            "created_at": vault_status["created_at"],
            "storage_efficiency": self._calculate_efficiency(),
        }
    
    def _calculate_efficiency(self) -> float:
        """Calculate storage efficiency percentage."""
        if self.vault.capacity == 0:
            return 0.0
        return (self.vault.current_items / self.vault.capacity) * 100


# Convenience functions
def create_storage_protocols(
    vault: VaultSimulator = None, capacity: int = 1000
) -> StorageProtocols:
    """Create storage protocols instance."""
    protocols = StorageProtocols(vault)
    protocols.initialize_vault(capacity=capacity)
    return protocols


def quick_store(module_id: str, data: Dict[str, Any], capacity: int = 1000) -> bool:
    """Quick store function for module data."""
    protocols = create_storage_protocols(capacity=capacity)
    return protocols.store_module_data(module_id, data)


def quick_retrieve(module_id: str, capacity: int = 1000) -> Optional[Dict[str, Any]]:
    """Quick retrieve function for module data."""
    protocols = create_storage_protocols(capacity=capacity)
    return protocols.retrieve_module_data(module_id)
