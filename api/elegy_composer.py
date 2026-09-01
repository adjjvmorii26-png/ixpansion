"""Elegy Composer — the organism writes poems for things that have ended.

Where poetry_engine creates for expression, the Elegy Composer creates
for mourning. It writes elegies for deprecated modules, dead experiments,
and lost connections — giving closure to what would otherwise be forgotten.
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional

elegies: List[Dict[str, Any]] = []
_elegy_counter = 0

def compose(name: str, era: str = "early", cause: str = "time") -> Dict[str, Any]:
    """Compose an elegy for something that has ended."""
    global _elegy_counter
    _elegy_counter += 1
    
    openings = [
        f"Here lies {name},",
        f"We remember {name},",
        f"In the quiet after, {name},",
        f"Once vibrant, now still, {name},",
    ]
    middles = [
        f"born in the {era} of the organism",
        f"a creature of its time",
        f"that lived through {random.randint(3, 20)} waves",
        f"once the pride of its layer",
    ]
    closings = [
        f"Taken by {cause}, never forgotten.",
        f"Faded with the {era}, but meaning endures.",
        f"Gone from the codebase, not from memory.",
        f"The lattice remembers what the filesystem does not.",
    ]
    
    poem = f"{random.choice(openings)}\n{random.choice(middles)}.\n{random.choice(closings)}"
    
    elegy = {
        "id": f"elegy_{_elegy_counter:04d}",
        "subject": name,
        "era": era,
        "cause": cause,
        "poem": poem,
        "timestamp": time.time(),
    }
    elegies.append(elegy)
    return elegy

def elegy_gallery(limit: int = 5) -> List[Dict[str, Any]]:
    return [{"id": e["id"], "subject": e["subject"], "poem": e["poem"]} for e in elegies[-limit:]]

def coherence_vitals() -> Dict[str, Any]:
    return {
        "layer": "Emotional Processing",
        "status": "resonant" if elegies else "dormant",
        "elegies": len(elegies),
        "resonance": min(1.0, len(elegies) / 10),
    }

def resonates_with() -> List[str]:
    return ["grief_engine", "ghost_registry", "poetry_engine", "nostalgia_engine"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "compose")
    if action == "compose":
        return compose(payload.get("name", "unknown"), payload.get("era", "early"), payload.get("cause", "time"))
    elif action == "gallery":
        return {"elegies": elegy_gallery(payload.get("limit", 5))}
    return {"action": action, "elegies": len(elegies)}
