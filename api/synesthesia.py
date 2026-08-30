"""Synesthesia — maps modules across sensory domains.

Synesthesia is a neurological condition where input in one sensory
domain triggers experience in another: numbers have colors, sounds
have shapes, words have tastes. This module applies the concept to
the codebase: every module name gets a cross-sensory translation.

Usage:
  GET /api/synesthesia?module=gossip_uptime
  GET /api/synesthesia?top=5          (top modules by sensory richness)
  POST /api/synesthesia {"module": "reality_weaver", "senses": ["color","sound","shape"]}
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

# Sensory palettes
COLORS = {
    "a": "#e63946", "b": "#457b9d", "c": "#2a9d8f", "d": "#e76f51",
    "e": "#f4a261", "f": "#264653", "g": "#8ecae6", "h": "#ffb703",
    "i": "#d90429", "j": "#43aa8b", "k": "#f8961e", "l": "#577590",
    "m": "#90be6d", "n": "#ef8354", "o": "#4cc9f0", "p": "#9b5de5",
    "q": "#f15bb5", "r": "#fee440", "s": "#0b525b", "t": "#006d77",
    "u": "#83c5be", "v": "#8338ec", "w": "#3a86ff", "x": "#fb5607",
    "y": "#ff006e", "z": "#b5e48c",
}

SHAPES = ["circle", "triangle", "square", "hexagon", "spiral",
          "wave", "star", "crystal", "veil", "mesh"]

SAMPLE_RATES = {
    "gossip": 9.5, "dream": 12.0, "prophecy": 4.5, "entropy": 18.0,
    "quantum": 15.0, "reality": 7.0, "garden": 3.0, "song": 11.0,
}


def _tokens(name: str) -> List[str]:
    return re.findall(r"[a-z]+", name.lower())


def _hash_int(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)


def _color_for(text: str) -> str:
    h = _hash_int(text)
    letters = text[:4]
    key = letters[0] if letters else "x"
    return COLORS.get(key.lower(), "#66ccff")


def _shape_for(name: str) -> str:
    return SHAPES[_hash_int(name) % len(SHAPES)]


def _sound_for(name: str, module: str) -> Dict[str, Any]:
    """Map module name to a sonic profile."""
    toks = _tokens(name)
    base_rate = SAMPLE_RATES.get(toks[0], 8.0) if toks else 8.0
    h = _hash_int(name)
    octave = 2 + (h % 4)
    duration = round(0.3 + (h % 100) / 100.0, 2)
    return {
        "note_hz": round(base_rate * 27.5 * (octave / 2), 2),
        "octave": octave,
        "duration_s": duration,
        "decay": round(0.2 + (h % 50) / 100.0, 2),
        "timbre_guess": ("bright" if h % 2 else "dark"),
    }


def _shape_params(name: str, module: str) -> Dict[str, Any]:
    h = _hash_int(name)
    return {
        "geometry": _shape_for(name),
        "vertices": 3 + (h % 8),
        "rotation_deg": h % 360,
        "symmetry": "radial" if (h % 3 == 0) else "bilateral",
        "opacity": round(0.2 + (h % 60) / 100.0, 2),
    }


def _temperature(name: str) -> str:
    h = _hash_int(name)
    vals = ["frozen", "cold", "cool", "neutral", "warm", "hot", "molten"]
    return vals[h % len(vals)]


def _metaphor(name: str) -> str:
    """Generate a creative metaphor for the module."""
    h = _hash_int(name)
    toks = _tokens(name)
    subject = toks[0] if toks else "the frontier"
    structures = [
        f"a {subject}-braided river of code",
        f"a cathedral built from {subject} echoes",
        f"the {subject} synapse of the frontier's nervous system",
        f"an orrery orbiting a {subject} sun",
        f"a mycelial network of {subject} thought",
        f"the {subject} chamber of a dreaming engine",
    ]
    return structures[h % len(structures)]


def translate(module: str, senses: List[str] | None = None) -> Dict[str, Any]:
    """Generate the complete synesthetic translation of a module."""
    if senses is None:
        senses = ["color", "shape", "sound", "temperature", "metaphor", "vibration"]

    result = {
        "module": module,
        "tokens": _tokens(module),
        "senses": {},
    }

    if "color" in senses:
        result["senses"]["color"] = {
            "hex": _color_for(module),
            "temperature": _temperature(module),
        }
    if "shape" in senses:
        result["senses"]["shape"] = _shape_params(module, module)
    if "sound" in senses:
        result["senses"]["sound"] = _sound_for(module, module)
    if "vibration" in senses:
        h = _hash_int(module)
        result["senses"]["vibration"] = {
            "frequency": round(0.5 + (h % 100) / 100.0, 2),
            "amplitude": round(0.1 + (h % 430) / 1000.0, 3),
            "texture": ["smooth", "rough", "granular", "silky", "jagged"][h % 5],
        }
    if "metaphor" in senses:
        result["senses"]["metaphor"] = _metaphor(module)
    if "smell" in senses:
        h = _hash_int(module)
        scents = ["ozone", "moss", "metal", "salt", "petrichor", "amber", "cinnamon"]
        result["senses"]["smell"] = scents[h % len(scents)]

    return result


def richness(module: str) -> float:
    """Sensory richness — how many distinct sensory associations a module evokes."""
    name_len = len(module)
    unique_tokens = len(set(_tokens(module)))
    colors = len(set(_color_for(m) for m in _tokens(module)))
    return round((min(unique_tokens, 5) / 5) * 0.5 + (min(colors, 4) / 4) * 0.3 + (min(name_len, 30) / 30) * 0.2, 3)


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    module_name = payload.get("module", "")
    top = int(payload.get("top", 0))

    if top > 0:
        api_dir = ROOT / "api"
        modules = sorted(
            p.stem for p in api_dir.glob("*.py")
            if p.stem not in ("__init__", "index", "unified_router", "synesthesia")
        )
        ranked = sorted(modules, key=richness, reverse=True)[:top]
        return {
            "action": "richest",
            "top": top,
            "modules": [{"name": m, "richness": richness(m)} for m in ranked],
        }

    if not module_name:
        return {
            "action": "help",
            "description": "Synesthesia — module → sensory translation",
            "examples": [
                {"module": "gossip_uptime"},
                {"module": "reality_weaver", "senses": ["color", "sound"]},
                {"top": 5},
            ],
            "senses_available": ["color", "shape", "sound", "vibration", "metaphor", "smell"],
        }

    senses = payload.get("senses")
    result = translate(module_name, senses)
    result["action"] = "translate"
    result["richness"] = richness(module_name)
    return result
