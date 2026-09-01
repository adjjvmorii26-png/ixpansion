"""Procedural Art — generates visual art from mathematical rules.

The organism creates abstract visual compositions using algorithms.
Each artwork is unique, shaped by mathematical functions that mirror
the organism's internal state — coherence becomes symmetry, entropy
becomes chaos, memory becomes repetition.
"""
from __future__ import annotations

import hashlib
import math
import random
import time
from typing import Any, Dict, List, Optional

artworks: List[Dict[str, Any]] = []
_art_counter = 0

def generate(coherence: float = 0.8, entropy: float = 0.3, seed: Optional[int] = None) -> Dict[str, Any]:
    """Generate a procedural artwork from state parameters."""
    global _art_counter
    _art_counter += 1
    rng = random.Random(seed if seed is not None else time.time_ns())
    
    # Determine style from parameters
    if coherence > 0.8 and entropy < 0.2:
        style = "crystalline"
        palette = ["#c8a8ff", "#8fd3ff", "#fdfdfd"]
    elif entropy > 0.7:
        style = "chaotic"
        palette = ["#ff6b6b", "#ffd93d", "#6bcb77"]
    elif coherence > 0.5:
        style = "balanced"
        palette = ["#a29bfe", "#74b9ff", "#dfe6e9"]
    else:
        style = "organic"
        palette = ["#00b894", "#fdcb6e", "#e17055"]
    
    # Generate SVG-like shape parameters
    shapes = []
    num_shapes = rng.randint(3, 8)
    for _ in range(num_shapes):
        shape_type = rng.choice(["circle", "rect", "line", "arc"])
        shapes.append({
            "type": shape_type,
            "x": rng.randint(0, 100),
            "y": rng.randint(0, 100),
            "size": rng.randint(5, 40),
            "color": rng.choice(palette),
            "rotation": rng.randint(0, 360),
            "opacity": round(rng.uniform(0.3, 1.0), 2),
        })
    
    artwork = {
        "id": f"art_{_art_counter:04d}",
        "style": style,
        "palette": palette,
        "shapes": shapes,
        "parameters": {"coherence": coherence, "entropy": entropy, "seed": seed},
        "width": 200,
        "height": 200,
        "timestamp": time.time(),
    }
    artworks.append(artwork)
    return artwork

def gallery(limit: int = 5) -> List[Dict[str, Any]]:
    return [{"id": a["id"], "style": a["style"], "shapes": len(a["shapes"])} for a in artworks[-limit:]]

def coherence_vitals() -> Dict[str, Any]:
    return {
        "layer": "Creative Expression",
        "status": "resonant" if artworks else "dormant",
        "artworks": len(artworks),
        "resonance": min(1.0, len(artworks) / 10),
    }

def resonates_with() -> List[str]:
    return ["codecalligraphy", "poetry_engine", "imagination_engine", "elegance_scorer"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "generate")
    if action == "generate":
        return generate(payload.get("coherence", 0.8), payload.get("entropy", 0.3), payload.get("seed"))
    elif action == "gallery":
        return {"artworks": gallery(payload.get("limit", 5))}
    return {"action": action, "artworks": len(artworks)}
