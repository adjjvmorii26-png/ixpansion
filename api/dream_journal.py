"""Dream Journal — records and analyzes dream sequences over time.

Every dream leaves traces. The Dream Journal tracks patterns across
dreams, identifies recurring themes, and reveals the organism's
evolving subconscious landscape.
"""
from __future__ import annotations

import time
from collections import Counter
from typing import Any, Dict, List, Optional

entries: List[Dict[str, Any]] = []
_entry_counter = 0

def record(title: str, symbols: List[str], emotion: str = "neutral",
           clarity: float = 0.5) -> Dict[str, Any]:
    """Record a dream journal entry."""
    global _entry_counter
    _entry_counter += 1
    entry = {
        "id": f"journal_{_entry_counter:04d}",
        "title": title,
        "symbols": symbols,
        "emotion": emotion,
        "clarity": round(clarity, 3),
        "recorded": time.time(),
    }
    entries.append(entry)
    return entry

def analyze() -> Dict[str, Any]:
    """Analyze patterns across all journal entries."""
    if not entries:
        return {"entries": 0, "themes": {}, "emotional_arc": [], "avg_clarity": 0}
    
    all_symbols = []
    for e in entries:
        all_symbols.extend(e["symbols"])
    theme_freq = Counter(all_symbols).most_common(10)
    
    emotional_arc = [e["emotion"] for e in entries[-10:]]
    
    avg_clarity = sum(e["clarity"] for e in entries) / len(entries)
    
    return {
        "entries": len(entries),
        "top_themes": theme_freq,
        "emotional_arc": emotional_arc,
        "avg_clarity": round(avg_clarity, 3),
        "first_dream": entries[0]["title"] if entries else None,
        "latest_dream": entries[-1]["title"] if entries else None,
    }

def coherence_vitals() -> Dict[str, Any]:
    a = analyze()
    return {
        "layer": "Subconscious Processing",
        "status": "resonant" if a["entries"] > 0 else "dormant",
        "entries": a["entries"],
        "avg_clarity": a["avg_clarity"],
        "resonance": min(1.0, a["entries"] / 15),
    }

def resonates_with() -> List[str]:
    return ["dream_weaver", "lucid_dreamer", "memory_palace", "subconscious_layer"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "analyze")
    if action == "record":
        return record(payload.get("title", "untitled"), payload.get("symbols", []),
                     payload.get("emotion", "neutral"), payload.get("clarity", 0.5))
    elif action == "analyze":
        return {"analysis": analyze()}
    elif action == "recent":
        return {"entries": entries[-payload.get("limit", 5):]}
    return {"action": action, "status": "journaling"}
