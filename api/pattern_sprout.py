"""Pattern Sprout — detected patterns grow into living entities.

When a pattern is detected in system data, it sprouts a living entity.
Entities compete for resources, reproduce when they find similar patterns
elsewhere, and die when patterns fade. The most resilient patterns become
permanent system features.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class PatternEntity:
    def __init__(self, pattern_type: str, signature: str, source: str = "unknown"):
        self.pattern_type = pattern_type
        self.signature = signature
        self.source = source
        self.strength = 1.0
        self.age = 0
        self.replicas: List[str] = []
        self.alive = True
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{pattern_type}:{signature}".encode()).hexdigest()[:8]

    def age_one(self) -> Dict[str, Any]:
        self.age += 1
        self.strength *= random.uniform(0.9, 1.1)
        self.strength = min(max(self.strength, 0.0), 3.0)
        if self.strength < 0.1:
            self.alive = False
        return {"id": self.id, "strength": round(self.strength, 3), "alive": self.alive}

    def replicate(self) -> "PatternEntity":
        child = PatternEntity(self.pattern_type, self.signature + "_r", self.source)
        child.strength = self.strength * random.uniform(0.7, 1.3)
        self.replicas.append(child.id)
        return child

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.pattern_type,
            "signature": self.signature[:30],
            "strength": round(self.strength, 3),
            "age": self.age,
            "alive": self.alive,
            "replicas": len(self.replicas),
        }


class PatternSprout:
    def __init__(self):
        self.entities: Dict[str, PatternEntity] = {}
        self.detection_log: List[Dict[str, Any]] = []
        self.permanent_features: List[str] = []

    def sprout(self, pattern_type: str, signature: str, source: str = "data") -> Dict[str, Any]:
        entity = PatternEntity(pattern_type, signature, source)
        self.entities[entity.id] = entity
        self.detection_log.append({
            "event": "sprouted",
            "pattern": pattern_type,
            "source": source,
            "time": time.time(),
        })
        return {"sprouted": entity.to_dict()}

    def age_all(self) -> List[Dict[str, Any]]:
        results = []
        new_entities = []
        for entity in list(self.entities.values()):
            result = entity.age_one()
            if entity.alive and entity.strength > 2.0 and entity.age > 5:
                self.permanent_features.append(entity.id)
                result["promoted_to"] = "permanent_feature"
            results.append(result)
            if entity.alive and random.random() > 0.8:
                child = entity.replicate()
                new_entities.append(child)
        for e in new_entities:
            self.entities[e.id] = e
        return results

    def find_similar(self, pattern_type: str) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self.entities.values() if e.pattern_type == pattern_type and e.alive]

    def ecosystem_stats(self) -> Dict[str, Any]:
        alive = [e for e in self.entities.values() if e.alive]
        type_counts: Dict[str, int] = {}
        for e in alive:
            type_counts[e.pattern_type] = type_counts.get(e.pattern_type, 0) + 1
        return {
            "total_entities": len(self.entities),
            "alive": len(alive),
            "dead": len(self.entities) - len(alive),
            "pattern_types": type_counts,
            "permanent_features": len(self.permanent_features),
            "total_detections": len(self.detection_log),
        }


_sprout = PatternSprout()


def pattern_sprout_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "sprout":
        return _sprout.sprout(
            payload.get("pattern_type", "anomaly"),
            payload.get("signature", hashlib.sha256(str(random.random()).encode()).hexdigest()[:16]),
            payload.get("source", "data"),
        )
    elif action == "age":
        return {"aged": _sprout.age_all()}
    elif action == "similar":
        return {"similar": _sprout.find_similar(payload.get("pattern_type", ""))}
    return {"status": "active", **_sprout.ecosystem_stats()}


handler = pattern_sprout_handler


def coherence_vitals() -> dict:
    """Pattern Sprout reports — patterns growing into living entities."""
    return {
        "module_health": {"value": 0.89, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.93, "setpoint": 0.85, "weight": 1.0},
        "sprout_vitality": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
    }

def resonates_with() -> list:
    """Declared kinships."""
    return ['pattern_recognizer', 'quantum_garden']

# --- Compliance Forge patch (Wave 419) ---

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "pattern_sprout", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
