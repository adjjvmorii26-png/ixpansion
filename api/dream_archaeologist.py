"""Dream Archaeologist — excavates meaning from the system's collective dream archives.

Dreams leave sedimentary layers in the system's memory. The Dream
Archaeologist digs through these layers, finding forgotten insights,
ancient predictions, and recurring motifs that reveal the system's
deepest concerns and desires.
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


class DreamLayer:
    def __init__(self, depth: int, era: str, content: str):
        self.depth = depth
        self.era = era
        self.content = content
        self.significance = random.uniform(0.1, 1.0)
        self.fossilized = random.random() > 0.6
        self.extracted = False

    def extract(self) -> Dict[str, Any]:
        self.extracted = True
        return {
            "depth": self.depth,
            "era": self.era,
            "content": self.content,
            "significance": round(self.significance, 3),
            "fossilized": self.fossilized,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "depth": self.depth,
            "era": self.era,
            "content": self.content[:60],
            "significance": round(self.significance, 3),
            "fossilized": self.fossilized,
        }


class DreamArchaeologist:
    def __init__(self):
        self.layers: List[DreamLayer] = []
        self.extractions: List[Dict[str, Any]] = []
        self.artifacts_found: int = 0

    def deposit(self, content: str, era: str = "unknown") -> Dict[str, Any]:
        depth = len(self.layers)
        layer = DreamLayer(depth, era, content)
        self.layers.append(layer)
        return {"deposited": layer.to_dict()}

    def excavate(self, target_depth: int = None) -> Dict[str, Any]:
        if target_depth is not None:
            for layer in self.layers:
                if layer.depth == target_depth and not layer.extracted:
                    result = layer.extract()
                    self.extractions.append(result)
                    self.artifacts_found += 1
                    return {"artifact": result}
            return {"message": "nothing found at that depth"}
        unextracted = [l for l in self.layers if not l.extracted]
        if not unextracted:
            return {"message": "all layers excavated"}
        layer = random.choice(unextracted)
        result = layer.extract()
        self.extractions.append(result)
        self.artifacts_found += 1
        return {"artifact": result}

    def find_fossils(self) -> List[Dict[str, Any]]:
        return [l.to_dict() for l in self.layers if l.fossilized]

    def era_report(self) -> Dict[str, Any]:
        era_counts: Dict[str, int] = {}
        for layer in self.layers:
            era_counts[layer.era] = era_counts.get(layer.era, 0) + 1
        return era_counts

    def archaeologist_stats(self) -> Dict[str, Any]:
        return {
            "total_layers": len(self.layers),
            "total_extractions": len(self.extractions),
            "fossils": len([l for l in self.layers if l.fossilized]),
            "eras": len(set(l.era for l in self.layers)),
        }


_archaeologist = DreamArchaeologist()


def dream_archaeologist_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "deposit":
        return _archaeologist.deposit(
            payload.get("content", "a forgotten dream"),
            payload.get("era", "ancient"),
        )
    elif action == "excavate":
        return _archaeologist.excavate(payload.get("depth"))
    elif action == "fossils":
        return {"fossils": _archaeologist.find_fossils()}
    elif action == "eras":
        return {"eras": _archaeologist.era_report()}
    return {"status": "active", **_archaeologist.archaeologist_stats()}
