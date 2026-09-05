"""Muse Inspiration — channels random creative impulses into agent work.

The Muse is a probabilistic creativity engine. It injects random but
coherent creative impulses: color suggestions, word associations,
structural metaphors, and conceptual bridges. Agents that接受 the Muse
produce more novel work.
"""
from __future__ import annotations

import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

COLORS = ["crimson", "sapphire", "emerald", "amber", "violet", "obsidian", "pearl", "coral"]
WORDS = ["echo", "fractal", "crystal", "prism", "nexus", "void", "bloom", "ember", "rift", "veil"]
METAPHORS = [
    "like a river finding its way to the sea",
    "as a constellation rearranging itself",
    "like light bending through a prism",
    "as roots growing toward water",
    "like a melody resolving into harmony",
    "as smoke writing stories in the air",
]
STRUCTURES = ["spiral", "web", "tree", "wave", "lattice", "constellation", "river", "circuit"]


class MuseInspiration:
    def __init__(self):
        self.inspirations: List[Dict[str, Any]] = []
        self.adopted: List[Dict[str, Any]] = []
        self.muse_stats = {"total_improvisations": 0, "total_adoptions": 0}

    def improvise(self, context: str = "", agent_id: str = "seeker") -> Dict[str, Any]:
        self.muse_stats["total_improvisations"] += 1
        inspiration = {
            "color": random.choice(COLORS),
            "word": random.choice(WORDS),
            "metaphor": random.choice(METAPHORS),
            "structure": random.choice(STRUCTURES),
            "mood": random.choice(["contemplative", "eager", "mysterious", "playful", "profound"]),
            "suggestion": f"Try approaching {context or 'the problem'} as a {random.choice(STRUCTURES)}, using {random.choice(COLORS)} energy.",
            "timestamp": time.time(),
            "context": context,
            "agent_id": agent_id,
        }
        self.inspirations.append(inspiration)
        return {"inspiration": inspiration}

    def adopt(self, inspiration_idx: int, agent_id: str) -> Dict[str, Any]:
        if 0 <= inspiration_idx < len(self.inspirations):
            inspiration = self.inspirations[inspiration_idx]
            adoption = {
                "inspiration": inspiration,
                "adopted_by": agent_id,
                "adopted_at": time.time(),
            }
            self.adopted.append(adoption)
            self.muse_stats["total_adoptions"] += 1
            return {"adopted": adoption}
        return {"error": "invalid inspiration index"}

    def recent_inspirations(self, count: int = 5) -> List[Dict[str, Any]]:
        return self.inspirations[-count:]

    def muse_report(self) -> Dict[str, Any]:
        return {
            **self.muse_stats,
            "adoption_rate": round(
                self.muse_stats["total_adoptions"] / max(self.muse_stats["total_improvisations"], 1), 3
            ),
        }


_muse = MuseInspiration()


def muse_inspiration_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "improvise":
        return _muse.improvise(payload.get("context", ""), payload.get("agent_id", "seeker"))
    elif action == "adopt":
        return _muse.adopt(payload.get("index", 0), payload.get("agent_id", "creator"))
    elif action == "recent":
        return {"inspirations": _muse.recent_inspirations(payload.get("count", 5))}
    return {"status": "active", **_muse.muse_report()}


handler = muse_inspiration_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "0", "module": "muse_inspiration"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "muse_inspiration", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
