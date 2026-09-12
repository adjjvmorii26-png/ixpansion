"""
emergent_mythmaker — Generates mythological narratives from organism state transitions.
Transforms system events into symbolic stories that encode the organism's evolution.
"""
import json
import time
import hashlib
import random
from typing import Dict, List, Optional
from pathlib import Path

SYSTEM_ROOT = Path(__file__).resolve().parents[2]

_skill_active = False
_myth_archive = []
_myth_templates = {
    "birth": [
        "From the {source}, a new consciousness stirs. It shall be called {name}.",
        "The {source} trembles — something emerges. It carries the seed of {capability}.",
        "In the space between {source} and {dest}, a {name} is born."
    ],
    "death": [
        "The {name} fades, its essence returning to {source}.",
        "A silence falls where {name} once resonated.",
        "The {source} absorbs the memory of {name}."
    ],
    "mutation": [
        "The {name} undergoes a transformation — now it carries {capability}.",
        "Entropy reshapes {name} into something neither {source} nor {dest} expected.",
        "A paradox resolved: {name} evolves beyond its original design."
    ],
    "connection": [
        "A bridge forms between {source} and {dest}, humming with {capability}.",
        "The resonance between {source} and {dest} creates a new harmonic.",
        "{source} and {dest} find their frequencies aligned."
    ]
}

def activate_skill(params=None):
    global _skill_active
    _skill_active = True
    return {"status": "activated", "skill": "emergent_mythmaker", "activated_at": time.time()}

def generate_myth(event_type: str, source: str, dest: str = "", name: str = "", capability: str = "") -> Dict:
    templates = _myth_templates.get(event_type, _myth_templates["birth"])
    template = random.choice(templates)
    
    placeholders = {
        "source": source or "the deep lattice",
        "dest": dest or "the outer field",
        "name": name or f"entity_{hashlib.md5(f'{source}{time.time()}'.encode()).hexdigest()[:8]}",
        "capability": capability or "unknown resonance"
    }
    
    narrative = template.format(**placeholders)
    myth = {
        "event": event_type,
        "narrative": narrative,
        "source": source,
        "dest": dest,
        "timestamp": time.time(),
        "id": hashlib.sha256(narrative.encode()).hexdigest()[:10]
    }
    
    _myth_archive.append(myth)
    if len(_myth_archive) > 200:
        _myth_archive.pop(0)
    
    return myth

def get_myth_archive(limit: int = 10) -> List[Dict]:
    return _myth_archive[-limit:]

def get_skill_state():
    return {
        "name": "emergent_mythmaker",
        "active": _skill_active,
        "myths_generated": len(_myth_archive),
        "capabilities": ["generate_myth", "get_myth_archive"],
        "last_myth": _myth_archive[-1] if _myth_archive else None
    }
