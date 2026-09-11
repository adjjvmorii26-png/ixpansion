"""Evolution Tracker - Monitors module evolution across organism waves."""

import json
import hashlib
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ModuleSnapshot:
    """Snapshot of a module at a specific wave."""
    wave: int
    module_id: str
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    parent_module: Optional[str] = None
    mutation_type: str = "unknown"
    hash_signature: str = ""
    
    def __post_init__(self):
        if not self.hash_signature:
            self.hash_signature = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute hash signature of module data."""
        return hashlib.sha256(
            json.dumps(self.data, sort_keys=True).encode()
        ).hexdigest()[:16]


class EvolutionTracker:
    """Tracks module evolution across organism waves."""
    
    def __init__(self, storage_protocols=None):
        self.snapshots: Dict[str, List[ModuleSnapshot]] = defaultdict(list)
        self.wave_metadata: Dict[int, Dict[str, Any]] = {}
        self.lineage_graph: Dict[str, List[str]] = defaultdict(list)
        self.storage = storage_protocols
        self.current_wave = 404  # Starting from latest known wave
    
    def set_current_wave(self, wave: int) -> None:
        """Set the current wave for tracking."""
        self.current_wave = wave
    
    def record_module(self, module_id: str, data: Dict[str, Any], 
                      mutation_type: str = "mutation", 
                      parent_module: Optional[str] = None) -> ModuleSnapshot:
        """Record a module snapshot at the current wave."""
        snapshot = ModuleSnapshot(
            wave=self.current_wave,
            module_id=module_id,
            data=data,
            parent_module=parent_module,
            mutation_type=mutation_type,
        )
        
        self.snapshots[module_id].append(snapshot)
        
        # Update lineage
        if parent_module:
            self.lineage_graph[parent_module].append(module_id)
        
        # Store in vault if storage is available
        if self.storage:
            self._persist_snapshot(snapshot)
        
        return snapshot
    
    def _persist_snapshot(self, snapshot: ModuleSnapshot) -> None:
        """Persist snapshot to storage."""
        key = f"evolution:{snapshot.module_id}:wave_{snapshot.wave}"
        self.storage.store(key, {
            "wave": snapshot.wave,
            "module_id": snapshot.module_id,
            "data": snapshot.data,
            "timestamp": snapshot.timestamp,
            "parent_module": snapshot.parent_module,
            "mutation_type": snapshot.mutation_type,
            "hash_signature": snapshot.hash_signature,
        })
    
    def get_module_history(self, module_id: str) -> List[ModuleSnapshot]:
        """Get complete evolution history for a module."""
        return self.snapshots.get(module_id, [])
    
    def get_wave_modules(self, wave: int) -> List[ModuleSnapshot]:
        """Get all modules that existed in a specific wave."""
        result = []
        for module_id, snapshots in self.snapshots.items():
            for snap in snapshots:
                if snap.wave == wave:
                    result.append(snap)
        return result
    
    def analyze_mutation_patterns(self, module_id: str) -> Dict[str, Any]:
        """Analyze mutation patterns for a module."""
        history = self.get_module_history(module_id)
        if len(history) < 2:
            return {"error": "Insufficient history for analysis"}
        
        patterns = {
            "total_mutations": len(history) - 1,
            "mutation_types": defaultdict(int),
            "hash_changes": [],
            "parent_lineage": [],
        }
        
        for i in range(1, len(history)):
            prev = history[i-1]
            curr = history[i]
            
            patterns["mutation_types"][curr.mutation_type] += 1
            patterns["hash_changes"].append({
                "from_wave": prev.wave,
                "to_wave": curr.wave,
                "hash_changed": prev.hash_signature != curr.hash_signature,
                "prev_hash": prev.hash_signature,
                "curr_hash": curr.hash_signature,
            })
            
            if curr.parent_module:
                patterns["parent_lineage"].append(curr.parent_module)
        
        # Convert defaultdict to regular dict
        patterns["mutation_types"] = dict(patterns["mutation_types"])
        
        return patterns
    
    def get_lineage_tree(self, root_module: str) -> Dict[str, Any]:
        """Get the full lineage tree starting from a root module."""
        def build_tree(module_id: str) -> Dict[str, Any]:
            children = self.lineage_graph.get(module_id, [])
            return {
                "module_id": module_id,
                "children": [build_tree(child) for child in children],
                "history_length": len(self.snapshots.get(module_id, [])),
            }
        
        return build_tree(root_module)
    
    def record_wave_metadata(self, wave: int, metadata: Dict[str, Any]) -> None:
        """Record metadata about a wave."""
        self.wave_metadata[wave] = metadata
    
    def get_wave_report(self, wave: int) -> Dict[str, Any]:
        """Generate a report for a specific wave."""
        modules = self.get_wave_modules(wave)
        metadata = self.wave_metadata.get(wave, {})
        
        return {
            "wave": wave,
            "module_count": len(modules),
            "modules": [
                {
                    "module_id": m.module_id,
                    "mutation_type": m.mutation_type,
                    "parent": m.parent_module,
                    "hash": m.hash_signature,
                }
                for m in modules
            ],
            "metadata": metadata,
        }
    
    def export_evolution_log(self) -> Dict[str, Any]:
        """Export complete evolution log for archival."""
        return {
            "tracker_version": "1.0",
            "exported_at": time.time(),
            "current_wave": self.current_wave,
            "total_modules": len(self.snapshots),
            "modules": {
                module_id: [
                    {
                        "wave": s.wave,
                        "data": s.data,
                        "timestamp": s.timestamp,
                        "parent_module": s.parent_module,
                        "mutation_type": s.mutation_type,
                        "hash_signature": s.hash_signature,
                    }
                    for s in snapshots
                ]
                for module_id, snapshots in self.snapshots.items()
            },
            "wave_metadata": self.wave_metadata,
            "lineage_graph": dict(self.lineage_graph),
        }


def create_evolution_tracker(storage_protocols=None) -> EvolutionTracker:
    """Factory function to create evolution tracker."""
    return EvolutionTracker(storage_protocols)
