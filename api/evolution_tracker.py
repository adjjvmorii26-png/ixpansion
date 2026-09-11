# Wave 405: Evolution Tracker Organ
# Tracks module evolution across organism waves

"""Evolution Tracker - Organ for monitoring module evolution and lineage."""

import json
import hashlib
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ModuleSnapshot:
    wave: int
    module_id: str
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    parent_module: Optional[str] = None
    mutation_type: str = "unknown"
    hash_signature: str = ""
    
    def __post_init__(self):
        if not self.hash_signature:
            self.hash_signature = hashlib.sha256(
                json.dumps(self.data, sort_keys=True).encode()
            ).hexdigest()[:16]


class EvolutionTracker:
    """Tracks module evolution across organism waves."""
    
    def __init__(self, storage_protocols=None):
        self.snapshots: Dict[str, List[ModuleSnapshot]] = defaultdict(list)
        self.wave_metadata: Dict[int, Dict[str, Any]] = {}
        self.lineage_graph: Dict[str, List[str]] = defaultdict(list)
        self.storage = storage_protocols
        self.current_wave = 404
    
    def set_current_wave(self, wave: int):
        self.current_wave = wave
    
    def record_module(self, module_id: str, data: Dict[str, Any],
                      mutation_type: str = "mutation",
                      parent_module: Optional[str] = None) -> ModuleSnapshot:
        snapshot = ModuleSnapshot(
            wave=self.current_wave,
            module_id=module_id,
            data=data,
            parent_module=parent_module,
            mutation_type=mutation_type,
        )
        self.snapshots[module_id].append(snapshot)
        if parent_module:
            self.lineage_graph[parent_module].append(module_id)
        return snapshot
    
    def get_module_history(self, module_id: str) -> List[ModuleSnapshot]:
        return self.snapshots.get(module_id, [])
    
    def get_wave_modules(self, wave: int) -> List[ModuleSnapshot]:
        result = []
        for snapshots in self.snapshots.values():
            for snap in snapshots:
                if snap.wave == wave:
                    result.append(snap)
        return result
    
    def analyze_mutation_patterns(self, module_id: str) -> Dict[str, Any]:
        history = self.get_module_history(module_id)
        if len(history) < 2:
            return {"error": "Insufficient history"}
        patterns = {"total_mutations": len(history) - 1, "mutation_types": defaultdict(int), "hash_changes": []}
        for i in range(1, len(history)):
            prev, curr = history[i-1], history[i]
            patterns["mutation_types"][curr.mutation_type] += 1
            patterns["hash_changes"].append({
                "from_wave": prev.wave, "to_wave": curr.wave,
                "hash_changed": prev.hash_signature != curr.hash_signature,
            })
        patterns["mutation_types"] = dict(patterns["mutation_types"])
        return patterns
    
    def get_lineage_tree(self, root_module: str) -> Dict[str, Any]:
        visited = set()
        def build(node_id: str) -> Dict[str, Any]:
            if node_id in visited:
                return {"module_id": node_id, "children": [], "history_length": len(self.snapshots.get(node_id, [])), "circular": True}
            visited.add(node_id)
            children = self.lineage_graph.get(node_id, [])
            return {
                "module_id": node_id,
                "children": [build(c) for c in children],
                "history_length": len(self.snapshots.get(node_id, [])),
            }
        return build(root_module)
    
    def record_wave_metadata(self, wave: int, metadata: Dict[str, Any]):
        self.wave_metadata[wave] = metadata
    
    def get_wave_report(self, wave: int) -> Dict[str, Any]:
        modules = self.get_wave_modules(wave)
        return {
            "wave": wave,
            "module_count": len(modules),
            "modules": [
                {"module_id": m.module_id, "mutation_type": m.mutation_type,
                 "parent": m.parent_module, "hash": m.hash_signature}
                for m in modules
            ],
            "metadata": self.wave_metadata.get(wave, {}),
        }
    
    def export_evolution_log(self) -> Dict[str, Any]:
        return {
            "tracker_version": "1.0",
            "exported_at": time.time(),
            "current_wave": self.current_wave,
            "total_modules": len(self.snapshots),
            "modules": {
                m: [{"wave": s.wave, "data": s.data, "timestamp": s.timestamp,
                     "parent_module": s.parent_module, "mutation_type": s.mutation_type,
                     "hash_signature": s.hash_signature} for s in snaps]
                for m, snaps in self.snapshots.items()
            },
            "wave_metadata": self.wave_metadata,
            "lineage_graph": dict(self.lineage_graph),
        }


_tracker = None

def get_tracker() -> EvolutionTracker:
    global _tracker
    if _tracker is None:
        _tracker = EvolutionTracker()
    return _tracker


def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    """Vercel-compatible handler."""
    action = payload.get("action", "report")
    tracker = get_tracker()
    
    if action == "set_wave":
        wave = payload.get("wave", 405)
        tracker.set_current_wave(wave)
        return {"status": "wave_set", "current_wave": tracker.current_wave}
    
    elif action == "record":
        module_id = payload.get("module_id", "")
        data = payload.get("data", {})
        mut_type = payload.get("mutation_type", "mutation")
        parent = payload.get("parent_module")
        snap = tracker.record_module(module_id, data, mut_type, parent)
        return {"status": "recorded", "wave": snap.wave, "hash": snap.hash_signature}
    
    elif action == "history":
        module_id = payload.get("module_id", "")
        history = tracker.get_module_history(module_id)
        return {"status": "ok", "module_id": module_id, "history_length": len(history)}
    
    elif action == "patterns":
        module_id = payload.get("module_id", "")
        patterns = tracker.analyze_mutation_patterns(module_id)
        return {"status": "ok", "patterns": patterns}
    
    elif action == "lineage":
        module_id = payload.get("module_id", "")
        tree = tracker.get_lineage_tree(module_id)
        return {"status": "ok", "lineage": tree}
    
    elif action == "wave_report":
        wave = payload.get("wave", tracker.current_wave)
        report = tracker.get_wave_report(wave)
        return {"status": "ok", "report": report}
    
    elif action == "export":
        return {"status": "ok", "export": tracker.export_evolution_log()}
    
    return {"status": "error", "message": f"Unknown action: {action}"}
