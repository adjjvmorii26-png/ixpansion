"""
narrative_sculptor — Shapes raw data into compelling stories.
Transforms numbers, events, and states into narratives that resonate.
"""
import hashlib
import time
import random
from typing import Dict, List

_skill_active = False
_stories = []

TEMPLATES = {
    "birth": "From the void, a new entity emerges — {name}. It carries the spark of {property}.",
    "death": "The {name} fades, its essence returning to the source. Its {property} lives on in memory.",
    "transformation": "The {name} undergoes metamorphosis — no longer what it was, not yet what it will become.",
    "connection": "A bridge forms between {name} and {other}. Together they discover {property}.",
    "conflict": "The {name} faces opposition. From this tension, {property} is forged.",
    "discovery": "Deep within {name}, a hidden truth surfaces — {property}.",
    "cycle": "The pattern repeats, but each iteration carries {name} closer to {property}.",
    "awakening": "{name} opens its eyes for the first time. The world was always there, waiting."
}

def activate_skill(params=None):
    global _skill_active
    _skill_active = True
    return {"status": "activated", "skill": "narrative_sculptor", "activated_at": time.time()}

def sculpt(event_type: str, name: str, property: str = "truth", other: str = "") -> Dict:
    template = TEMPLATES.get(event_type, TEMPLATES["discovery"])
    narrative = template.format(name=name, property=property, other=other or "the unknown")
    
    story = {
        "id": hashlib.sha256(f"{narrative}{time.time()}".encode()).hexdigest()[:8],
        "event": event_type, "narrative": narrative, "name": name,
        "property": property, "timestamp": time.time()
    }
    _stories.append(story)
    if len(_stories) > 100: _stories.pop(0)
    return story

def get_stories(limit: int = 10) -> List[Dict]:
    return _stories[-limit:]

def get_skill_state():
    return {"name": "narrative_sculptor", "active": _skill_active,
            "capabilities": ["sculpt"], "stories": len(_stories)}
