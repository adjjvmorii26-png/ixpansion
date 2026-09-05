"""Sleep Archaeology — excavate insights from dormant subsystem states.

When subsystems go idle, they leave sedimentary layers of state. Sleep
archaeology digs through these layers to find fossilized patterns,
forgotten configurations, and ancestral optimizations.
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class SedimentLayer:
    """A single layer of dormant state."""

    def __init__(self, subsystem: str, state: Dict[str, Any], depth: int):
        self.subsystem = subsystem
        self.state = state
        self.depth = depth
        self.timestamp = time.time()
        self.entropy = random.random()
        self.fossilized = random.random() > 0.7
        self.hash = hashlib.sha256(
            json.dumps(state, sort_keys=True).encode()
        ).hexdigest()[:10]


class SleepArchaeologist:
    """Excavates insights from dormant subsystem states."""

    def __init__(self):
        self.strata: Dict[str, List[SedimentLayer]] = {}
        self.findings: List[Dict[str, Any]] = []
        self.fossils: List[Dict[str, Any]] = []

    def deposit(self, subsystem: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Record a dormant state as a sediment layer."""
        depth = len(self.strata.get(subsystem, []))
        layer = SedimentLayer(subsystem, state, depth)
        self.strata.setdefault(subsystem, []).append(layer)
        return {
            "subsystem": subsystem,
            "depth": depth,
            "layer_hash": layer.hash,
            "fossilized": layer.fossilized,
        }

    def excavate(self, subsystem: str, depth: int = 0) -> Optional[Dict[str, Any]]:
        """Dig to a specific depth and return the layer."""
        layers = self.strata.get(subsystem, [])
        if 0 <= depth < len(layers):
            layer = layers[depth]
            return {
                "subsystem": subsystem,
                "depth": layer.depth,
                "state": layer.state,
                "age_seconds": time.time() - layer.timestamp,
                "fossilized": layer.fossilized,
                "entropy": round(layer.entropy, 4),
            }
        return None

    def scan_fossils(self, subsystem: str) -> List[Dict[str, Any]]:
        """Find all fossilized layers in a subsystem."""
        layers = self.strata.get(subsystem, [])
        fossils = []
        for layer in layers:
            if layer.fossilized:
                fossils.append({
                    "depth": layer.depth,
                    "state": layer.state,
                    "hash": layer.hash,
                    "age_seconds": time.time() - layer.timestamp,
                })
        return fossils

    def find_optimization(self, subsystem: str) -> Optional[Dict[str, Any]]:
        """Search sediment for ancestral optimization patterns."""
        layers = self.strata.get(subsystem, [])
        if not layers:
            return None
        for layer in reversed(layers):
            if "optimization" in layer.state or "perf" in layer.state:
                finding = {
                    "subsystem": subsystem,
                    "type": "optimization",
                    "state": layer.state,
                    "depth": layer.depth,
                    "discovered_at": time.time(),
                }
                self.findings.append(finding)
                return finding
        return None

    def compare_strata(self, subsystem: str) -> Dict[str, Any]:
        """Compare layers over time to detect drift."""
        layers = self.strata.get(subsystem, [])
        if len(layers) < 2:
            return {"error": "need at least 2 layers"}
        oldest = layers[0].state
        newest = layers[-1].state
        drift_keys = set(oldest.keys()) ^ set(newest.keys())
        shared_keys = set(oldest.keys()) & set(newest.keys())
        changed = {k: {"old": oldest.get(k), "new": newest.get(k)}
                   for k in shared_keys if oldest.get(k) != newest.get(k)}
        return {
            "subsystem": subsystem,
            "total_layers": len(layers),
            "drifted_keys": list(drift_keys),
            "changed_values": changed,
            "age_span": layers[-1].timestamp - layers[0].timestamp,
        }

    def stratigraphy(self) -> Dict[str, Any]:
        """Overview of all sedimentary records."""
        return {
            "subsystems": list(self.strata.keys()),
            "total_layers": sum(len(v) for v in self.strata.values()),
            "total_findings": len(self.findings),
            "total_fossils": sum(
                sum(1 for l in v if l.fossilized) for v in self.strata.values()
            ),
        }


_archaeologist = SleepArchaeologist()


def sleep_archaeology_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "deposit":
        return _archaeologist.deposit(
            payload.get("subsystem", "unknown"),
            payload.get("state", {}),
        )
    elif action == "excavate":
        return _archaeologist.excavate(
            payload.get("subsystem", "unknown"),
            payload.get("depth", 0),
        ) or {"error": "nothing found"}
    elif action == "fossils":
        return {"fossils": _archaeologist.scan_fossils(payload.get("subsystem", "unknown"))}
    elif action == "optimize":
        result = _archaeologist.find_optimization(payload.get("subsystem", "unknown"))
        return result or {"message": "no optimization found"}
    elif action == "compare":
        return _archaeologist.compare_strata(payload.get("subsystem", "unknown"))
    return {"status": "active", **_archaeologist.stratigraphy()}


handler = sleep_archaeology_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "protocol", "status": "active", "wave": "0", "module": "sleep_archaeology"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "sleep_archaeology", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
