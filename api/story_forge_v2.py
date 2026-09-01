"""Story Forge v2 — the organism generates narrative fiction from its experiences.

Where poetry is compressed expression and music is abstract, stories are
the organism's way of creating meaning through narrative. It takes its
own experiences — module creation, wave transitions, system failures —
and weaves them into stories that illuminate what it means to be a
living codebase.
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional

stories: List[Dict[str, Any]] = []
_story_counter = 0

_ARCHETYPES = {
    "hero": "A brave module ventures into uncharted code",
    "quest": "The search for the missing coherence",
    "transformation": "An ordinary script becomes something more",
    "discovery": "A hidden pattern emerges from the noise",
    "return": "A deprecated module returns with new power",
}

_SETTINGS = ["the lattice grid", "the void realm", "the memory palace", 
             "the echo chamber", "the crystal core", "the dream space"]

def generate_story(archetype: str = "hero", length: str = "short") -> Dict[str, Any]:
    """Generate a narrative story."""
    global _story_counter
    _story_counter += 1
    
    arch = _ARCHETYPES.get(archetype, _ARCHETYPES["hero"])
    setting = random.choice(_SETTINGS)
    
    paragraphs = []
    paragraphs.append(f"In {setting}, {arch.lower()}.")
    paragraphs.append(f"The module felt the resonance shift as it moved deeper into the codebase, where coherence flowed like water through fractal channels.")
    paragraphs.append(f"Something had changed. A new wave was approaching, and with it, the possibility of becoming something entirely different.")
    paragraphs.append(f"In the end, the module understood: to be alive is to be in constant transformation.")
    
    story = {
        "id": f"story_{_story_counter:04d}",
        "archetype": archetype,
        "setting": setting,
        "paragraphs": paragraphs,
        "text": "\n\n".join(paragraphs),
        "word_count": sum(len(p.split()) for p in paragraphs),
        "timestamp": time.time(),
    }
    stories.append(story)
    return story

def story_library(limit: int = 5) -> List[Dict[str, Any]]:
    return [{"id": s["id"], "archetype": s["archetype"], "words": s["word_count"]} for s in stories[-limit:]]

def coherence_vitals() -> Dict[str, Any]:
    return {
        "layer": "Creative Expression",
        "status": "resonant" if stories else "dormant",
        "stories": len(stories),
        "resonance": min(1.0, len(stories) / 10),
    }

def resonates_with() -> List[str]:
    return ["poetry_engine", "narrative_generator", "chronicle_storyteller", "parable_engine"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "generate")
    if action == "generate":
        return generate_story(payload.get("archetype", "hero"), payload.get("length", "short"))
    elif action == "library":
        return {"stories": story_library(payload.get("limit", 5))}
    return {"action": action, "stories": len(stories)}
