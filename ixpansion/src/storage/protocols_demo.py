"""
Storage Protocols Demo for ixpansion Organism

This demonstration shows the complete storage system in action,
including vault management, protocol compliance, and inter-vault synchronization.
"""

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage import (
    VaultSimulator, StorageProtocols, create_vault,
    quick_store, quick_retrieve
)
import json
import time

print("=" * 70)
print("IXPANSION ORGANISM - STORAGE PROTOCOLS DEMONSTRATION")
print("=" * 70)

# =============================================================================
# 1. VAULT CREATION AND BASIC OPERATIONS
# =============================================================================
print("\n--- 1. VAULT CREATION AND BASIC OPERATIONS ---")
vault = create_vault(capacity=100)
print(f"Vault ID: {vault.vault_id}")
print(f"Initial status: {json.dumps(vault.status(), indent=2)}")

# Store various module data
modules = [
    ("agent_core", {"type": "agent", "level": 5, "status": "active"}),
    ("entropy_regulator", {"type": "controller", "chaos_level": 0.3}),
    ("pulse_loop", {"type": "heartbeat", "frequency": "1Hz"}),
    ("fusion_reactor", {"type": "reactor", "mode": "balanced"}),
]

for module_id, data in modules:
    result = quick_store(module_id, data)
    print(f"Stored {module_id}: {result}")

# Retrieve and display
print("\nRetrieved modules:")
for module_id, _ in modules:
    data = quick_retrieve(module_id)
    if data:
        print(f"  {module_id}: {data}")
    else:
        print(f"  {module_id}: NOT FOUND")

# =============================================================================
# 2. STORAGE PROTOCOLS WITH INTEGRITY CHECKING
# =============================================================================
print("\n--- 2. STORAGE PROTOCOLS WITH INTEGRITY CHECKING ---")
protocols = StorageProtocols(vault)

# Store module data with protocols
protocol_modules = [
    ("consciousness_aurora", {"dimensions": 12, "frequency": "alpha"}),
    ("paradox_gravity_well", {"distortion": 0.7, "stability": "high"}),
    ("self_reference_engine", {"loop_depth": 5, "status": "operational"}),
]

for module_id, data in protocol_modules:
    stored = protocols.store_module_data(module_id, data)
    print(f"Protocol store {module_id}: {stored}")

# Retrieve with integrity verification
print("\nProtocol-retrieved modules:")
for module_id, _ in protocol_modules:
    data = protocols.retrieve_module_data(module_id)
    if data:
        # Check for integrity warnings
        if "_hash_warning" in data:
            print(f"  {module_id}: ⚠️ INTEGRITY WARNING - {data['_hash_warning']}")
        else:
            print(f"  {module_id}: ✓ {data}")
    else:
        print(f"  {module_id}: NOT FOUND")

# =============================================================================
# 3. VAULT REPORT AND EFFICIENCY
# =============================================================================
print("\n--- 3. VAULT REPORT AND EFFICIENCY ---")
report = protocols.generate_vault_report()
print(json.dumps(report, indent=2, default=str))

# Test efficiency calculation
efficiency = protocols._calculate_efficiency()
print(f"\nStorage efficiency: {efficiency:.1f}%")

# =============================================================================
# 4. INTER-VAULT SYNCHRONIZATION
# =============================================================================
print("\n--- 4. INTER-VAULT SYNCHRONIZATION ---")
# Create a second vault
vault2 = create_vault(capacity=100)
protocols2 = StorageProtocols(vault2)

# Store different data in each vault
protocols.store_module_data("unique_module_a", {"data": "only_in_vault_1"})
protocols2.store_module_data("unique_module_b", {"data": "only_in_vault_2"})

# Sync state
sync_report = protocols.sync_vault_state(vault2)
print(f"Synced keys: {sync_report['synced_keys']}")
print(f"Conflicts: {sync_report['conflicts']}")
print(f"Missing in other vault: {sync_report['missing_in_other']}")
print(f"Errors: {sync_report['errors']}")

# =============================================================================
# 5. ADVANCED FEATURES DEMONSTRATION
# =============================================================================
print("\n--- 5. ADVANCED FEATURES DEMONSTRATION ---")

# Test vault locking
print("Testing vault locking...")
vault.lock()
print(f"Vault locked: {vault.status()['locked']}")

vault.unlock()
print(f"Vault unlocked: {vault.status()['locked']}")

# Test current_items tracking
print(f"\nCurrent items tracked: {vault.current_items}/{vault.capacity}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("DEMONSTRATION COMPLETE")
print("=" * 70)
print("""
Storage System Capabilities:
• Vault creation with configurable capacity
• Protocol-compliant module data storage
• Integrity verification via payload hashing
• Inter-vault synchronization
• Efficiency tracking and reporting
• Vault locking/unlocking mechanism
• Current items tracking
• Cross-vault conflict detection
• Comprehensive status reporting

All modules integrate seamlessly with the ixpansion organism architecture.
""")
