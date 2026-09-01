"""Codecalligraphy — visual art generated from code structure.

Each module produces a unique glyph based on its function signatures,
imports, and complexity. The organism creates a living gallery of its
own visual identity, where every piece of code becomes a piece of art.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
gallery: Dict[str, Dict[str, Any]] = {}

_GLYPH_CHARS = "·∘○◎◉●◐◑◒◓◔◕◖◗◘◙◚◛◧◨╔╗╚╝╠╣╦╩┼─│┌┐└┘├┤┬┴"

def _hash_to_glyph(code_hash: str) -> str:
    """Convert a hex hash into a visual glyph string."""
    glyph = ""
    for i in range(0, min(len(code_hash), 12), 2):
        idx = int(code_hash[i:i+2], 16) % len(_GLYPH_CHARS)
        glyph += _GLYPH_CHARS[idx]
    return glyph

def _hash_to_color(code_hash: str) -> str:
    """Convert hash to a CSS color."""
    r = int(code_hash[0:2], 16)
    g = int(code_hash[2:4], 16)
    b = int(code_hash[4:6], 16)
    return f"#{r:02x}{g:02x}{b:02x}"

def _analyze_complexity(code: str) -> Dict[str, float]:
    """Analyze code complexity for visual parameters."""
    lines = code.split("\n")
    indent_depths = [len(l) - len(l.lstrip()) for l in lines if l.strip()]
    avg_indent = sum(indent_depths) / max(len(indent_depths), 1)
    max_indent = max(indent_depths) if indent_depths else 0
    density = len([l for l in lines if l.strip()]) / max(len(lines), 1)
    return {
        "line_count": len(lines),
        "avg_indent": round(avg_indent, 1),
        "max_indent": max_indent,
        "density": round(density, 3),
        "complexity_score": round(avg_indent * density * 10, 1),
    }

def generate_glyph(module_name: str) -> Dict[str, Any]:
    """Generate a unique calligraphic glyph for a module."""
    api_dir = ROOT / "api"
    target = api_dir / f"{module_name}.py"
    if not target.exists():
        return {"error": f"module {module_name} not found"}
    
    code = target.read_text(encoding="utf-8")
    h = hashlib.sha256(code.encode()).hexdigest()[:16]
    glyph = _hash_to_glyph(h)
    color = _hash_to_color(h)
    complexity = _analyze_complexity(code)
    
    # Generate SVG-like description
    radius = 20 + complexity["complexity_score"]
    strokes = complexity["line_count"]
    
    art = {
        "module": module_name,
        "glyph": glyph,
        "color": color,
        "hash": h,
        "complexity": complexity,
        "visual": {
            "radius": round(radius, 1),
            "stroke_count": strokes,
            "symmetry": "radial" if complexity["max_indent"] < 8 else "asymmetric",
            "palette": [color, _hash_to_color(h[4:10]), _hash_to_color(h[8:14])],
        },
    }
    gallery[module_name] = art
    return art

def gallery_stats() -> Dict[str, Any]:
    """Return gallery statistics."""
    return {
        "artworks": len(gallery),
        "modules_available": len(list((ROOT / "api").glob("*.py"))) - 1,
        "top_complex": sorted(
            [{"name": k, "score": v["complexity"]["complexity_score"]} 
             for k, v in gallery.items()],
            key=lambda x: x["score"], reverse=True
        )[:5],
    }

def coherence_vitals() -> Dict[str, Any]:
    stats = gallery_stats()
    return {
        "layer": "Aesthetic Expression",
        "status": "resonant" if stats["artworks"] > 0 else "dormant",
        "artworks": stats["artworks"],
        "resonance": min(1.0, stats["artworks"] / 20),
    }

def resonates_with() -> List[str]:
    return ["elegance_scorer", "beauty_index", "symmetry_detector", "aesthetic_manifesto"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "stats")
    if action == "generate":
        return generate_glyph(payload.get("module", ""))
    elif action == "gallery":
        return {"gallery": list(gallery.values())}
    return {"action": action, "stats": gallery_stats()}
