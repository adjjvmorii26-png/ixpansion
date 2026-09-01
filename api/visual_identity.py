"""Wave 213 — The Organism Draws Itself.

A self-portraiture engine that generates dynamic SVG crests
representing the organism's current state. Each render is a
unique snapshot: living module count shapes the spiral arms,
resonance average determines the halo brightness, wave number
encodes the central glyph. This is code-native identity —
no imagegen required.
"""
from __future__ import annotations

import math
from typing import Any, Dict


def _color_from_resonance(r: float) -> str:
    if r > 0.8:
        return "#fff3a0"   # halo gold
    if r > 0.5:
        return "#c8a8ff"   # violet mist
    if r > 0.3:
        return "#8fd3ff"   # kinsih blue
    return "#1a0f29"       # primeval black


def _spiral_points(arms: int, cx: float, cy: float, t_max: float, step: float = 0.15) -> str:
    pts = []
    for arm in range(arms):
        for t in [i * step for i in range(int(t_max / step))]:
            angle = t + (2 * math.pi * arm / arms)
            r = 3 * t
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            pts.append(f"{x:.1f},{y:.1f}")
    return " ".join(pts)


def _glyph(wave: int) -> str:
    glyphs = "\u2609\u263D\u2641\u2642\u2643\u2644\u2645\u2646\u2647\u2648"
    return glyphs[wave % len(glyphs)]


def _svg(
    wave: int,
    modules: int,
    resonance: float,
    glyph: str,
    size: int = 400,
) -> str:
    cx, cy = size / 2, size / 2
    halo_color = _color_from_resonance(resonance)
    arms = max(3, min(modules // 60, 12))
    t_max = min(20, modules / 15.0)
    spiral = _spiral_points(arms, cx, cy, t_max)
    dash_animate = f"stroke-dasharray='600' stroke-dashoffset='0'"
    pulse_r = 28 + int(resonance * 22)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">'
        f'<rect width="{size}" height="{size}" fill="#0b0b0d"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{pulse_r + 30}" fill="none" stroke="{halo_color}" stroke-width="0.6" opacity="0.3"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{pulse_r + 16}" fill="none" stroke="{halo_color}" stroke-width="0.9" opacity="0.45"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{pulse_r}" fill="none" stroke="{halo_color}" stroke-width="1.2" opacity="0.7"/>'
        f'<polyline points="{spiral}" fill="none" stroke="{halo_color}" stroke-width="1" opacity="0.5" {dash_animate}/>'
        f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" font-size="32" fill="{halo_color}" opacity="0.9">{glyph}</text>'
        f'<text x="{cx}" y="{cy + 22}" text-anchor="middle" font-size="9" fill="#8fd3ff" opacity="0.6">W{wave} \u00b7 {modules} organs</text>'
        f'<text x="{cx}" y="{size - 16}" text-anchor="middle" font-size="8" fill="#c8a8ff" opacity="0.4">IXPANSION SELF-PORTRAIT \u00b7 r={resonance:.2f}</text>'
        f'</svg>'
    )


def coherence_vitals() -> Dict[str, Any]:
    return {
        "layer": "identity",
        "status": "resonant",
        "resonance": 0.71,
        "wave": 213,
    }


def resonates_with() -> list:
    return ["visual_identity", "crest", "logo", "svg", "portrait", "aesthetics"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    wave = int(context.get("wave", 213))
    modules = int(context.get("living_modules", 302))
    resonance = float(context.get("resonance", 0.66))
    glyph = _glyph(wave)
    svg = _svg(wave, modules, resonance, glyph)
    return {
        "format": "svg",
        "content_type": "image/svg+xml",
        "glyph": glyph,
        "arms": max(3, min(modules // 60, 12)),
        "resonance": resonance,
        "svg": svg,
    }
