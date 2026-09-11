# Wave 405: Storage Protocols Organ
# Protocol-compliant module data storage with integrity verification

"""Storage Protocols - Organ for protocol-compliant module data management."""

import json
import hashlib
import time
from typing import Dict, Any, Optional, List
from .storage_vault import StorageVault, get_vault


class StorageProtocols:
    """Storage protocols with integrity verification and cross-vault sync."""
    
    def __init__(self, vault: StorageVault = None):
        self.vault = vault or get_vault()
        self.protocol_version = "2.3.2"
        self.active_contracts: Dict[str, Any] = {}
    
    def store_module_data(self, module_id: str, data: Dict[str, Any]) -> bool:
        protocol_data = {
            "@type": "module_data",
            "module_id": module_id,
            "protocol_version": self.protocol_version,
            "timestamp": time.time(),
            "payload": data,
        }
        payload_hash = hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()[:16]
        protocol_data["payload_hash"] = payload_hash
        key = f"module:{module_id}"
        return self.vault.store(key, protocol_data)
    
    def retrieve_module_data(self, module_id: str) -> Optional[Dict[str, Any]]:
        key = f"module:{module_id}"
        raw_data = self.vault.retrieve(key)
        if raw_data is None:
            return None
        if raw_data.get("@type") != "module_data":
            return None
        stored_hash = raw_data.get("payload_hash")
        if stored_hash:
            payload = raw_data.get("payload", {})
            expected_hash = hashlib.sha256(
                json.dumps(payload, sort_keys=True).encode()
            ).hexdigest()[:16]
            if stored_hash != expected_hash:
                raw_data["_hash_warning"] = "integrity_check_failed"
        return raw_data.get("payload")
    
    def sync_vault_state(self, other_vault: StorageVault) -> Dict[str, Any]:
        sync_report = {"synced_keys": [], "conflicts": [], "missing_in_other": [], "errors": []}
        self_keys = set(self.vault.storage.keys())
        other_keys = set(other_vault.storage.keys())
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
        sync_report["missing_in_other"] = list(other_keys - self_keys)
        return sync_report
    
    def generate_vault_report(self) -> Dict[str, Any]:
        vault_status = self.vault.status()
        return {
            "protocol_version": self.protocol_version,
            "vault_id": vault_status["vault_id"],
            "capacity": vault_status["capacity"],
            "current_items": vault_status["current_items"],
            "locked": vault_status["locked"],
            "total_accesses": vault_status["total_accesses"],
            "created_at": vault_status["created_at"],
            "storage_efficiency": (vault_status["current_items"] / vault_status["capacity"]) * 100 if vault_status["capacity"] > 0 else 0.0,
        }


_protocols = None

def get_protocols() -> StorageProtocols:
    global _protocols
    if _protocols is None:
        _protocols = StorageProtocols()
    return _protocols


def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    """Vercel-compatible handler."""
    action = payload.get("action", "report")
    protocols = get_protocols()
    
    if action == "store_module":
        module_id = payload.get("module_id", "")
        data = payload.get("data", {})
        success = protocols.store_module_data(module_id, data)
        return {"status": "stored" if success else "failed", "module_id": module_id}
    
    elif action == "retrieve_module":
        module_id = payload.get("module_id", "")
        data = protocols.retrieve_module_data(module_id)
        return {"status": "retrieved" if data is not None else "not_found", "data": data}
    
    elif action == "report":
        return {"status": "ok", "report": protocols.generate_vault_report()}
    
    elif action == "sync":
        other_vault = StorageVault(capacity=100)
        sync_report = protocols.sync_vault_state(other_vault)
        return {"status": "synced", "report": sync_report}
    
    return {"status": "error", "message": f"Unknown action: {action}"}
