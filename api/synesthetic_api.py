"""Synesthetic API — transform any data into other sensory modalities.

Sound, color, texture, and taste mappings for data. Developers can
"listen" to their data or "feel" their API responses. Creates
multimodal representations for accessibility and creative exploration.

Usage:
    POST /api/synesthesia/sound     — data to sound frequencies
    POST /api/synesthesia/color     — data to color palette
    POST /api/synesthesia/texture   — data to tactile description
    POST /api/synesthesia/taste     — data to flavor profile
    GET  /api/synesthesia/preview   — full synesthetic preview
"""
from __future__ import annotations

import hashlib
import json
import math
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

COLOR_WHEEL = [
    "#FF0000", "#FF7700", "#FFFF00", "#77FF00",
    "#00FF00", "#00FF77", "#00FFFF", "#0077FF",
    "#0000FF", "#7700FF", "#FF00FF", "#FF0077",
]

OCTAVE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

TEXTURES = [
    "smooth silk", "rough sandpaper", "cool marble", "warm wood",
    "electric static", "liquid mercury", "crystalline ice", "soft moss",
    "braided steel", "woven carbon", "molten glass", "dry parchment",
]

TASTES = {
    "sweet": {"notes": ["honey", "vanilla", "caramel"], "mood": "joyful"},
    "sour": {"notes": ["lemon", "vinegar", "green apple"], "mood": "alert"},
    "salty": {"notes": ["ocean spray", "mineral", "sea salt"], "mood": "grounded"},
    "bitter": {"notes": ["dark chocolate", "espresso", "tonic"], "mood": "contemplative"},
    "umami": {"notes": ["miso", "parmesan", "soy"], "mood": "satisfied"},
    "metallic": {"notes": ["copper", "iron", "tin"], "mood": "focused"},
}


def _data_to_values(data: Any) -> List[float]:
    """Convert arbitrary data to 0-1 float values."""
    if isinstance(data, (int, float)):
        return [abs(data) % 1.0]
    if isinstance(data, list):
        return [abs(x) % 1.0 if isinstance(x, (int, float)) else hash(str(x)) % 1000 / 1000.0 for x in data]
    if isinstance(data, dict):
        return [hash(str(v)) % 1000 / 1000.0 for v in data.values()]
    return [hash(str(data)) % 1000 / 1000.0]


class SynestheticAPI:
    def __init__(self):
        self.history: List[Dict] = []

    def to_sound(self, data: Any) -> Dict:
        values = _data_to_values(data)
        frequencies = []
        for v in values:
            octave = int(v * 3) + 3  # Octaves 3-5
            note_idx = int(v * 12) % 12
            freq = 440 * (2 ** (octave - 4)) * (2 ** (note_idx / 12))
            frequencies.append({
                "frequency_hz": round(freq, 2),
                "note": f"{OCTAVE_NAMES[note_idx]}{octave}",
                "duration_ms": int(v * 500 + 100),
            })
        waveform = "sine" if len(values) < 5 else "complex"
        result = {
            "frequencies": frequencies,
            "waveform": waveform,
            "total_duration_ms": sum(f["duration_ms"] for f in frequencies),
            "key": OCTAVE_NAMES[int(sum(values) * 12) % 12],
        }
        self.history.append({"type": "sound", "timestamp": time.time()})
        return result

    def to_color(self, data: Any) -> Dict:
        values = _data_to_values(data)
        palette = []
        for v in values:
            idx = int(v * len(COLOR_WHEEL)) % len(COLOR_WHEEL)
            color = COLOR_WHEEL[idx]
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            palette.append({
                "hex": color, "rgb": [r, g, b],
                "luminance": round(luminance, 3),
            })
        avg_r = sum(p["rgb"][0] for p in palette) // max(len(palette), 1)
        avg_g = sum(p["rgb"][1] for p in palette) // max(len(palette), 1)
        avg_b = sum(p["rgb"][2] for p in palette) // max(len(palette), 1)
        result = {
            "palette": palette,
            "dominant_mood": "warm" if avg_r > avg_b else "cool" if avg_b > avg_r else "neutral",
            "avg_color": f"#{avg_r:02x}{avg_g:02x}{avg_b:02x}",
        }
        self.history.append({"type": "color", "timestamp": time.time()})
        return result

    def to_texture(self, data: Any) -> Dict:
        values = _data_to_values(data)
        avg = sum(values) / max(len(values), 1)
        variance = sum((v - avg) ** 2 for v in values) / max(len(values), 1)
        roughness = round(min(1.0, variance * 4), 3)
        temp = round(avg * 100, 1)
        texture_idx = int(avg * len(TEXTURES)) % len(TEXTURES)
        result = {
            "primary_texture": TEXTURES[texture_idx],
            "roughness": roughness,
            "temperature_celsius": temp,
            "tactile_description": f"A {TEXTURES[texture_idx]} surface, {'rough' if roughness > 0.5 else 'smooth'}, {'warm' if temp > 50 else 'cool'} to the touch",
            "hardness": round(roughness * 10, 1),
        }
        self.history.append({"type": "texture", "timestamp": time.time()})
        return result

    def to_taste(self, data: Any) -> Dict:
        values = _data_to_values(data)
        avg = sum(values) / max(len(values), 1)
        tastes = list(TASTES.keys())
        primary_idx = int(avg * len(tastes)) % len(tastes)
        primary = tastes[primary_idx]
        secondary_idx = (primary_idx + 2) % len(tastes)
        secondary = tastes[secondary_idx]
        intensity = round(avg * 10, 1)
        result = {
            "primary_taste": primary,
            "secondary_taste": secondary,
            "intensity": intensity,
            "notes": TASTES[primary]["notes"][:2],
            "mood": TASTES[primary]["mood"],
            "pairing_suggestion": f"{primary} with {secondary}",
            "flavor_text": f"A {intensity}/10 intensity {primary} flavor, {TASTES[primary]['mood']} in character",
        }
        self.history.append({"type": "taste", "timestamp": time.time()})
        return result

    def full_preview(self, data: Any) -> Dict:
        return {
            "sound": self.to_sound(data),
            "color": self.to_color(data),
            "texture": self.to_texture(data),
            "taste": self.to_taste(data),
        }


def handler(request, response):
    return {"modalities": ["sound", "color", "texture", "taste"]}


def demo():
    api = SynestheticAPI()
    print("=== Synesthetic API ===")
    sample = [0.3, 0.7, 0.1, 0.9, 0.5]
    sound = api.to_sound(sample)
    print(f"\nSound: {len(sound['frequencies'])} notes in {sound['key']}")
    for f in sound["frequencies"][:3]:
        print(f"  {f['note']} at {f['frequency_hz']}Hz ({f['duration_ms']}ms)")

    color = api.to_color(sample)
    print(f"\nColor: {color['dominant_mood']} mood, avg {color['avg_color']}")
    for p in color["palette"][:3]:
        print(f"  {p['hex']} (lum={p['luminance']})")

    texture = api.to_texture(sample)
    print(f"\nTexture: {texture['primary_texture']}, roughness={texture['roughness']}")

    taste = api.to_taste(sample)
    print(f"\nTaste: {taste['primary_taste']}, intensity={taste['intensity']}")
    print(f"  {taste['flavor_text']}")

    return {"modalities": 4}


if __name__ == "__main__":
    demo()
