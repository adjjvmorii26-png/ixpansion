# ixpansion Storage Module

## Overview
The Storage Module provides vault behavior simulation and storage protocols for the ixpansion organism architecture. It enables persistent module data management with integrity verification, inter-vault synchronization, and comprehensive reporting.

## Structure

### Files

1. **`__init__.py`** - Package initialization, exports key classes and functions
   - Exports: `VaultSimulator`, `StorageProtocols`, `create_vault`, `quick_store`, `quick_retrieve`

2. **`vault_simulator.py`** - Core vault implementation
   - `VaultSimulator` class - Manages vault lifecycle, storage, retrieval, and locking
   - `create_vault()` - Factory function for creating vault instances
   - Features: Capacity management, TTL support, item tracking, access logging

3. **`storage_protocols.py`** - Protocol layer for module data
   - `StorageProtocols` class - Protocol-compliant storage with integrity checking
   - `create_storage_protocols()` - Factory function
   - `quick_store()` / `quick_retrieve()` - Convenience functions
   - Features: Protocol versioning, payload hashing, inter-vault sync, conflict detection

4. **`protocols_demo.py`** - Demonstration script
   - Shows all capabilities in action
   - Can be run as: `python3 ixpansion/src/storage/protocols_demo.py`

## Key Features

### VaultSimulator
- **Capacity management**: Configurable storage limits with automatic eviction
- **TTL support**: Time-based expiration for temporary data
- **Locking mechanism**: Prevent modifications when locked
- **Item tracking**: Real-time current_items counter
- **Access logging**: Complete audit trail of all operations

### StorageProtocols
- **Protocol versioning**: Supports version 2.3.2 with backward compatibility
- **Integrity verification**: SHA-256 payload hashing for data integrity
- **Inter-vault sync**: Synchronize state between multiple vaults
- **Conflict detection**: Identify and report data conflicts
- **Efficiency reporting**: Calculate and report storage utilization

### Data Format
All module data stored through StorageProtocols follows this structure:
```json
{
  "@type": "module_data",
  "module_id": "string",
  "protocol_version": "2.3.2",
  "timestamp": float,
  "payload": {...},
  "payload_hash": "hex_string[:16]"
}
```

## Integration with ixpansion Organism

The storage module integrates with the broader organism architecture by:

1. **Module Data Persistence**: Store and retrieve module states, configurations, and metadata
2. **Cross-Realm Synchronization**: Ensure consistency across different organism realms
3. **Protocol Compliance**: Maintain standardized data formats across all modules
4. **Temporal Management**: Track module lifecycle and evolution states
5. **Access Auditing**: Maintain complete history of module data changes

## Usage Examples

### Basic Vault Operations
```python
from ixpansion.src.storage import create_vault, quick_store, quick_retrieve

# Create vault
vault = create_vault(capacity=200)

# Store data
result = quick_store("my_module", {"key": "value"})

# Retrieve data
data = quick_retrieve("my_module")
```

### Protocol-Compliant Storage
```python
from ixpansion.src.storage import StorageProtocols, create_vault

# Initialize with protocols
vault = create_vault(capacity=100)
protocols = StorageProtocols(vault)

# Store with protocol wrapping
protocols.store_module_data("agent_core", {"type": "agent", "level": 5})

# Retrieve with integrity verification
data = protocols.retrieve_module_data("agent_core")
```

### Inter-Vault Synchronization
```python
from ixpansion.src.storage import create_vault, StorageProtocols

# Create two vaults
vault1 = create_vault(capacity=100)
vault2 = create_vault(capacity=100)

# Initialize protocols
protocols1 = StorageProtocols(vault1)
protocols2 = StorageProtocols(vault2)

# Sync state between vaults
sync_report = protocols1.sync_vault_state(vault2)
```

## Performance

- **Storage efficiency**: Tracks and reports utilization percentage
- **Eviction policy**: LRU-style eviction when at capacity
- **Access speed**: Optimized for frequent read/write operations
- **Memory usage**: Minimal overhead with lazy loading

## Future Enhancements

 planned features:
- Encryption support for sensitive module data
- Compression for large payloads
- Distributed vault across multiple nodes
- Version history tracking
- Automated backup and recovery
- Integration with organism's wave cycle system
