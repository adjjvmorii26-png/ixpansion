"""Cognitive Heatmap — visualizes where collective thought energy concentrates.

A spatial map of the system's cognitive landscape. Hot zones are areas
of intense agent focus, cold zones are neglected regions. The heatmap
reveals emergent knowledge structures — spontaneous clusters of meaning
that no single agent planned.
"""
from __future__ import annotations

import math
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class CognitiveZone:
    def __init__(self, x: int, y: int, label: str = ""):
        self.x = x
        self.y = y
        self.label = label or f"zone_{x}_{y}"
        self.heat = 0.0
        self.contributors: List[str] = []
        self.history: List[float] = []

    def add_heat(self, agent_id: str, amount: float):
        self.heat += amount
        if agent_id not in self.contributors:
            self.contributors.append(agent_id)

    def cool(self, rate: float = 0.1):
        self.heat *= (1.0 - rate)
        self.history.append(self.heat)
        if len(self.history) > 50:
            self.history = self.history[-50:]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "position": [self.x, self.y],
            "heat": round(self.heat, 4),
            "contributors": len(self.contributors),
            "trend": "heating" if len(self.history) >= 2 and self.history[-1] > self.history[-2] else "cooling",
        }


class CognitiveHeatmap:
    def __init__(self, width: int = 10, height: int = 10):
        self.zones: Dict[str, CognitiveZone] = {}
        for x in range(width):
            for y in range(height):
                key = f"{x},{y}"
                self.zones[key] = CognitiveZone(x, y)
        self.tick_count = 0

    def activate(self, x: int, y: int, agent_id: str, intensity: float = 1.0) -> Dict[str, Any]:
        key = f"{x},{y}"
        if key not in self.zones:
            self.zones[key] = CognitiveZone(x, y)
        self.zones[key].add_heat(agent_id, intensity)
        self._propagate(x, y, intensity * 0.2)
        return {"activated": self.zones[key].to_dict()}

    def _propagate(self, x: int, y: int, amount: float):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                key = f"{x+dx},{y+dy}"
                if key in self.zones:
                    self.zones[key].heat += amount * 0.3

    def tick(self) -> Dict[str, Any]:
        self.tick_count += 1
        for zone in self.zones.values():
            zone.cool(0.05)
        hotspots = sorted(self.zones.values(), key=lambda z: z.heat, reverse=True)[:5]
        coldspots = sorted(self.zones.values(), key=lambda z: z.heat)[:3]
        return {
            "tick": self.tick_count,
            "hotspots": [z.to_dict() for z in hotspots if z.heat > 0],
            "coldspots": [z.to_dict() for z in coldspots],
        }

    def full_map(self) -> List[Dict[str, Any]]:
        return [z.to_dict() for z in self.zones.values() if z.heat > 0.01]

    def emerging_clusters(self) -> List[Dict[str, Any]]:
        hot_zones = [z for z in self.zones.values() if z.heat > 1.0]
        if not hot_zones:
            return []
        clusters: List[Dict[str, Any]] = []
        visited = set()
        for zone in hot_zones:
            key = f"{zone.x},{zone.y}"
            if key in visited:
                continue
            cluster = [zone]
            visited.add(key)
            for other in hot_zones:
                other_key = f"{other.x},{other.y}"
                if other_key in visited:
                    continue
                dist = math.sqrt((zone.x - other.x)**2 + (zone.y - other.y)**2)
                if dist <= 2:
                    cluster.append(other)
                    visited.add(other_key)
            if len(cluster) >= 2:
                clusters.append({
                    "center": zone.to_dict(),
                    "size": len(cluster),
                    "total_heat": round(sum(z.heat for z in cluster), 3),
                })
        return clusters

    def stats(self) -> Dict[str, Any]:
        active = [z for z in self.zones.values() if z.heat > 0.01]
        return {
            "total_zones": len(self.zones),
            "active_zones": len(active),
            "total_heat": round(sum(z.heat for z in self.zones.values()), 4),
            "peak_heat": round(max((z.heat for z in self.zones.values()), default=0), 4),
            "emerging_clusters": len(self.emerging_clusters()),
        }


_heatmap = CognitiveHeatmap()


def cognitive_heatmap_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "activate":
        return _heatmap.activate(
            payload.get("x", 5), payload.get("y", 5),
            payload.get("agent_id", "thinker"),
            payload.get("intensity", 1.0),
        )
    elif action == "tick":
        return _heatmap.tick()
    elif action == "map":
        return {"zones": _heatmap.full_map()}
    elif action == "clusters":
        return {"clusters": _heatmap.emerging_clusters()}
    return {"status": "active", **_heatmap.stats()}


handler = cognitive_heatmap_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "0", "module": "cognitive_heatmap"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "cognitive_heatmap", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
