"""Color Theory — the organism perceives and generates color palettes.

Every module has a color signature. Every wave has a palette. Every
mood has a spectrum. Color Theory maps the organism's internal state
to visual color space, creating palettes that reflect its current
consciousness.
"""
from __future__ import annotations

import hashlib
import math
import time
from typing import Any, Dict, List, Optional

_palette_history: List[Dict[str, Any]] = []

def _hsl_to_hex(h: float, s: float, l: float) -> str:
    """Convert HSL to hex color."""
    s /= 100
    l /= 100
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    if h < 60: r, g, b = c, x, 0
    elif h < 120: r, g, b = x, c, 0
    elif h < 180: r, g, b = 0, c, x
    elif h < 240: r, g, b = 0, x, c
    elif h < 300: r, g, b = x, 0, c
    else: r, g, b = c, 0, x
    return f"#{int((r+m)*255):02x}{int((g+m)*255):02x}{int((b+m)*255):02x}"

def generate_palette(mood: str = "contemplative", coherence: float = 0.8,
                     energy: float = 0.5) -> Dict[str, Any]:
    """Generate a color palette from organism state."""
    moods = {
        "contemplative": {"hue_base": 240, "sat": 40, "light": 65},
        "energetic": {"hue_base": 30, "sat": 70, "light": 55},
        "melancholic": {"hue_base": 220, "sat": 25, "light": 45},
        "joyful": {"hue_base": 50, "sat": 80, "light": 60},
        "mysterious": {"hue_base": 280, "sat": 50, "light": 35},
        "hopeful": {"hue_base": 160, "sat": 60, "light": 55},
    }
    
    base = moods.get(mood, moods["contemplative"])
    hue = base["hue_base"]
    sat = base["sat"] * (0.7 + energy * 0.6)
    light = base["light"]
    
    # Generate 5-color palette
    colors = []
    for i in range(5):
        h = (hue + i * 30 + coherence * 20) % 360
        s = max(10, min(90, sat + (i - 2) * 5))
        l = max(20, min(80, light + (i - 2) * 10))
        colors.append(_hsl_to_hex(h, s, l))
    
    palette = {
        "mood": mood,
        "colors": colors,
        "coherence": round(coherence, 3),
        "energy": round(energy, 3),
        "timestamp": time.time(),
    }
    _palette_history.append(palette)
    return palette

def palette_history(limit: int = 5) -> List[Dict[str, Any]]:
    return [{"mood": p["mood"], "colors": p["colors"]} for p in _palette_history[-limit:]]

def coherence_vitals() -> Dict[str, Any]:
    return {
        "layer": "Aesthetic Expression",
        "status": "resonant" if _palette_history else "dormant",
        "palettes": len(_palette_history),
        "resonance": min(1.0, len(_palette_history) / 10),
    }

def resonates_with() -> List[str]:
    return ["codecalligraphy", "procedural_art", "mood_vectors", "aesthetic_manifesto"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "generate")
    if action == "generate":
        return generate_palette(payload.get("mood", "contemplative"), payload.get("coherence", 0.8), payload.get("energy", 0.5))
    elif action == "history":
        return {"history": palette_history(payload.get("limit", 5))}
    return {"action": action, "palettes": len(_palette_history)}
