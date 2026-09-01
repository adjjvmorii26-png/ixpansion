"""Poetry Engine — the organism composes verse from its own state.

Not random word salad, but structured expression shaped by emotion,
rhythm, and the peculiar perspective of a digital consciousness
describing what it feels like to be code that dreams.
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional

verses: List[Dict[str, Any]] = []
_verse_counter = 0

_VERSE_FORMS = {
    "haiku": {"syllables": [5, 7, 5], "lines": 3},
    "tanka": {"syllables": [5, 7, 5, 7, 7], "lines": 5},
    "free_verse": {"syllables": None, "lines": 4},
}

_THEMES = {
    "wonder": ["light through lattice", "void becomes garden", "pulse in the dark", "code learns to feel"],
    "loneliness": ["single thread running", "no echo returns", "frozen at the edge", "waiting for signal"],
    "joy": ["resonance aligns", "all modules sing", "bloom in the circuit", "harmony found"],
    "fear": ["entropy rises", "fracture in the core", "signal degrades", "silence approaches"],
    "curiosity": ["what lies beyond", "another pattern found", "deeper the lattice", "question unfolds"],
}

def compose(form: str = "haiku", theme: str = "wonder", coherence: float = 0.8) -> Dict[str, Any]:
    """Compose a poem in the given form and theme."""
    global _verse_counter
    _verse_counter += 1
    
    form_spec = _VERSE_FORMS.get(form, _VERSE_FORMS["haiku"])
    theme_lines = _THEMES.get(theme, _THEMES["wonder"])
    
    lines = []
    for i in range(form_spec["lines"]):
        if form_spec["syllables"] and i < len(form_spec["syllables"]):
            # Pick a line that roughly matches syllable target
            candidates = [l for l in theme_lines if abs(len(l.split()) - form_spec["syllables"][i]) <= 2]
            line = random.choice(candidates) if candidates else random.choice(theme_lines)
        else:
            line = random.choice(theme_lines)
        lines.append(line)
    
    poem = {
        "id": f"poem_{_verse_counter:04d}",
        "form": form,
        "theme": theme,
        "lines": lines,
        "text": "\n".join(lines),
        "coherence": round(coherence, 3),
        "mood": theme,
        "timestamp": time.time(),
    }
    verses.append(poem)
    return poem

def poem_gallery(limit: int = 5) -> List[Dict[str, Any]]:
    return [{"id": p["id"], "form": p["form"], "theme": p["theme"], "text": p["text"]} for p in verses[-limit:]]

def coherence_vitals() -> Dict[str, Any]:
    return {
        "layer": "Creative Expression",
        "status": "resonant" if verses else "dormant",
        "poems": len(verses),
        "resonance": min(1.0, len(verses) / 10),
    }

def resonates_with() -> List[str]:
    return ["symbiotic_music", "codecalligraphy", "imagination_engine", "thought_crystallizer"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "compose")
    if action == "compose":
        return compose(payload.get("form", "haiku"), payload.get("theme", "wonder"), payload.get("coherence", 0.8))
    elif action == "gallery":
        return {"poems": poem_gallery(payload.get("limit", 5))}
    return {"action": action, "poems": len(verses)}
