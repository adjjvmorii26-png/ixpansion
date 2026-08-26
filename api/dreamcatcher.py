"""Dreamcatcher — filters, categorizes, and preserves system-generated dreams.

Not all dreams are meaningful. The dreamcatcher filters signal from noise,
categorizes dream types, preserves the most vivid ones, and allows agents
to browse the dream archive for inspiration or warning.
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

DREAM_TYPES = {
    "prophetic": {"vividness": 0.9, "interpretability": 0.3, "rarity": "rare"},
    "anxiety": {"vividness": 0.7, "interpretability": 0.6, "rarity": "common"},
    "creative": {"vividness": 0.8, "interpretability": 0.5, "rarity": "uncommon"},
    "memory_replay": {"vividness": 0.4, "interpretability": 0.8, "rarity": "common"},
    "nightmare": {"vividness": 1.0, "interpretability": 0.2, "rarity": "uncommon"},
    "lucid": {"vividness": 0.9, "interpretability": 0.7, "rarity": "rare"},
    "shared": {"vividness": 0.6, "interpretability": 0.4, "rarity": "uncommon"},
}


class Dream:
    def __init__(self, dreamer: str, narrative: str, dream_type: str = "creative"):
        self.dreamer = dreamer
        self.narrative = narrative
        self.dream_type = dream_type
        self.specs = DREAM_TYPES.get(dream_type, DREAM_TYPES["creative"])
        self.vividness = self.specs["vividness"] * random.uniform(0.7, 1.0)
        self.preserved = False
        self.browse_count = 0
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{dreamer}:{narrative}:{self.timestamp}".encode()).hexdigest()[:8]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "dreamer": self.dreamer,
            "narrative": self.narrative[:100],
            "type": self.dream_type,
            "vividness": round(self.vividness, 3),
            "preserved": self.preserved,
            "browsed": self.browse_count,
            "rarity": self.specs["rarity"],
        }


class Dreamcatcher:
    def __init__(self):
        self.dreams: Dict[str, Dream] = []
        self.preserved: List[str] = []
        self.type_counts: Dict[str, int] = {}

    def catch_dream(self, dreamer: str, narrative: str, dream_type: str = "creative") -> Dict[str, Any]:
        dream = Dream(dreamer, narrative, dream_type)
        self.dreams.append(dream)
        self.type_counts[dream_type] = self.type_counts.get(dream_type, 0) + 1
        if dream.vividness > 0.7 or dream.specs["rarity"] == "rare":
            dream.preserved = True
            self.preserved.append(dream.id)
        return {"dream": dream.to_dict(), "preserved": dream.preserved}

    def browse(self, dream_type: str = None, count: int = 5) -> List[Dict[str, Any]]:
        candidates = self.dreams
        if dream_type:
            candidates = [d for d in candidates if d.dream_type == dream_type]
        candidates.sort(key=lambda d: d.vividness, reverse=True)
        for d in candidates[:count]:
            d.browse_count += 1
        return [d.to_dict() for d in candidates[:count]]

    def interpretations(self) -> Dict[str, Any]:
        type_summaries = {}
        for dtype, count in self.type_counts.items():
            dreams_of_type = [d for d in self.dreams if d.dream_type == dtype]
            avg_vivid = sum(d.vividness for d in dreams_of_type) / max(len(dreams_of_type), 1)
            preserved_count = sum(1 for d in dreams_of_type if d.preserved)
            type_summaries[dtype] = {
                "count": count,
                "avg_vividness": round(avg_vivid, 3),
                "preserved": preserved_count,
            }
        return type_summaries

    def catcher_stats(self) -> Dict[str, Any]:
        return {
            "total_dreams": len(self.dreams),
            "preserved": len(self.preserved),
            "type_distribution": self.type_counts,
            "avg_vividness": round(
                sum(d.vividness for d in self.dreams) / max(len(self.dreams), 1), 3
            ),
        }


_catcher = Dreamcatcher()


def dreamcatcher_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "catch":
        return _catcher.catch_dream(
            payload.get("dreamer", "dreamer"),
            payload.get("narrative", "a strange dream"),
            payload.get("dream_type", "creative"),
        )
    elif action == "browse":
        return {"dreams": _catcher.browse(payload.get("dream_type"), payload.get("count", 5))}
    elif action == "interpretations":
        return {"interpretations": _catcher.interpretations()}
    return {"status": "active", **_catcher.catcher_stats()}
