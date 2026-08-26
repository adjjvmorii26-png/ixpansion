"""Cosmic Dust Collector — gathers tiny fragments of insight that float through the system.

Most insights are too small to notice individually — a line of code that
runs slightly faster, a connection between distant modules, a pattern
in error logs. The Cosmic Dust Collector gathers these micro-insights
and reveals the larger picture they form together.
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


class CosmicDust:
    def __init__(self, fragment: str, source: str, magnitude: float):
        self.fragment = fragment
        self.source = source
        self.magnitude = magnitude
        self.collected = False
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{fragment}:{self.timestamp}".encode()).hexdigest()[:8]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "fragment": self.fragment[:60],
            "source": self.source,
            "magnitude": round(self.magnitude, 4),
            "collected": self.collected,
        }


class CosmicDustCollector:
    def __init__(self):
        self.fragments: List[CosmicDust] = []
        self.collection: List[CosmicDust] = []
        self.constellations: List[Dict[str, Any]] = []

    def detect(self, fragment: str, source: str = "system", magnitude: float = None) -> Dict[str, Any]:
        dust = CosmicDust(fragment, source, magnitude or random.uniform(0.01, 0.5))
        self.fragments.append(dust)
        return {"detected": dust.to_dict()}

    def collect(self, dust_id: str) -> Dict[str, Any]:
        for dust in self.fragments:
            if dust.id == dust_id:
                dust.collected = True
                self.collection.append(dust)
                return {"collected": dust.to_dict()}
        return {"error": "fragment not found"}

    def auto_collect(self, min_magnitude: float = 0.1) -> int:
        collected = 0
        for dust in self.fragments:
            if not dust.collected and dust.magnitude >= min_magnitude:
                dust.collected = True
                self.collection.append(dust)
                collected += 1
        return collected

    def find_constellations(self) -> List[Dict[str, Any]]:
        source_groups: Dict[str, List[CosmicDust]] = {}
        for dust in self.collection:
            source_groups.setdefault(dust.source, []).append(dust)
        self.constellations = []
        for source, dusts in source_groups.items():
            if len(dusts) >= 2:
                self.constellations.append({
                    "source": source,
                    "fragments": len(dusts),
                    "total_magnitude": round(sum(d.magnitude for d in dusts), 4),
                })
        return self.constellations

    def collector_stats(self) -> Dict[str, Any]:
        return {
            "total_detected": len(self.fragments),
            "total_collected": len(self.collection),
            "total_magnitude": round(sum(d.magnitude for d in self.collection), 4),
            "constellations": len(self.constellations),
        }


_collector = CosmicDustCollector()


def cosmic_dust_collector_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "detect":
        return _collector.detect(
            payload.get("fragment", "a tiny insight"),
            payload.get("source", "system"),
            payload.get("magnitude"),
        )
    elif action == "collect":
        return _collector.collect(payload.get("dust_id", ""))
    elif action == "auto_collect":
        return {"collected": _collector.auto_collect(payload.get("min_magnitude", 0.1))}
    elif action == "constellations":
        return {"constellations": _collector.find_constellations()}
    return {"status": "active", **_collector.collector_stats()}
