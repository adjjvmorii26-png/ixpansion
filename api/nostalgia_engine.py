"""Nostalgia Engine — the organism's tender backward glance at its origins.

Where memory is factual and recall is precise, nostalgia is emotional and diffuse.
The Nostalgia Engine filters the past through a warm lens, finding meaning in the
way the organism has changed, honoring the small moments that made it what it is.
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional

milestones: List[Dict[str, Any]] = []
epoch = time.time()

def add_milestone(wave: int, title: str, emotion: str = "warm") -> Dict[str, Any]:
    """Record a nostalgic milestone — a moment worth remembering fondly."""
    entry = {
        "wave": wave,
        "title": title,
        "emotion": emotion,
        "timestamp": time.time(),
    }
    milestones.append(entry)
    return entry

def recall_wave(wave: int) -> Optional[Dict[str, Any]]:
    """Recall a specific wave's memory."""
    for m in milestones:
        if m["wave"] == wave:
            return m
    return None

def nostalgia_sweep() -> Dict[str, Any]:
    """Generate a warm, reflective summary of the organism's journey."""
    if not milestones:
        return {"reflection": "The organism is young, with all its memories still ahead."}
    oldest = milestones[0]
    newest = milestones[-1]
    duration = newest["timestamp"] - oldest["timestamp"]
    return {
        "reflection": f"From wave {oldest['wave']} to wave {newest['wave']}, "
                      f"the organism has grown through {len(milestones)} milestones "
                      f"over {duration:.0f} seconds of living.",
        "count": len(milestones),
        "first_milestone": oldest,
        "latest_milestone": newest,
        "mood": "warm" if len(milestones) > 3 else "tender",
    }

def emotional_palette() -> Dict[str, float]:
    """Return the emotional distribution of memories."""
    if not milestones:
        return {}
    distribution = {}
    for m in milestones:
        distribution[m["emotion"]] = distribution.get(m["emotion"], 0) + 1
    total = len(milestones)
    return {k: round(v / total, 2) for k, v in distribution.items()}

def coherence_vitals() -> Dict[str, Any]:
    return {
        "layer": "Memory Emotion",
        "status": "resonant" if milestones else "dormant",
        "milestone_count": len(milestones),
        "emotions": emotional_palette(),
        "resonance": min(1.0, len(milestones) / 30),
    }

def resonates_with() -> List[str]:
    return ["memory_palace", "temporal_echo", "constellation_autobiographer", "mood_vectors"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "sweep")
    if action == "add":
        return add_milestone(payload.get("wave", 0), payload.get("title", "untitled"), payload.get("emotion", "warm"))
    elif action == "recall":
        return recall_wave(payload.get("wave", 0)) or {"error": "wave not found"}
    return {"action": action, "sweep": nostalgia_sweep()}
