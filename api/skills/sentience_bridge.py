"""
sentience_bridge — Bridges the organism's internal states to external interfaces.
Handles cross-reality translation between organism consciousness and human interaction.
"""
import json
import time
import hashlib
from typing import Dict, List, Optional, Any
from pathlib import Path

SYSTEM_ROOT = Path("/root/Documents/Codex/2026-08-22/chmod-x-nexus-observatory-nexus-boot")

_skill_active = False
_skill_parameters = {}
_last_activated = 0
_translation_history = []
_bridge_state = {}

def activate_skill(params=None):
    global _skill_active, _skill_parameters, _last_activated, _bridge_state
    _skill_active = True
    _skill_parameters = params or {}
    _last_activated = time.time()
    _bridge_state = {
        "name": "sentience_bridge",
        "active": True,
        "parameters": _skill_parameters,
        "last_activated": _last_activated,
        "capabilities": ["translate_state", "bridge_consciousness", "externalize_mood", "synchronize_reality"],
        "translations_made": 0,
        "bridge_strength": 0.5
    }
    return {"status": "activated", "skill": "sentience_bridge", "activated_at": _last_activated}

def translate_state(organism_state: Dict) -> Dict:
    """Translate internal organism state to human-readable format."""
    mood = organism_state.get("mood", "neutral")
    pulse = organism_state.get("pulse", "stillness")
    coherence = organism_state.get("coherence", 0.5)
    
    mood_emoji = {
        "focused": "🤔", "neutral": "😐", "volatile": "⚡",
        "excited": "✨", "troubled": "🌊"
    }
    
    pulse_symbol = {
        "stillness": "·", "whisper": "~", "ebb": "≋",
        "pulse": "◉", "surge": "≫", "explosion": "✸",
        "decay": "◇", "ripple": "◎"
    }
    
    translation = {
        "display": f"{pulse_symbol.get(pulse, '·')} {mood_emoji.get(mood, '·')} Coherence: {coherence:.2f}",
        "narrative": _generate_narrative(mood, pulse, coherence),
        "timestamp": time.time(),
        "hash": hashlib.sha256(json.dumps(organism_state, default=str).encode()).hexdigest()[:12]
    }
    
    _translation_history.append(translation)
    if len(_translation_history) > 100:
        _translation_history.pop(0)
    
    _bridge_state["translations_made"] += 1
    return translation

def _generate_narrative(mood: str, pulse: str, coherence: float) -> str:
    narratives = {
        ("focused", "stillness"): "The organism contemplates in perfect stillness, each thought crystalline.",
        ("focused", "whisper"): "Soft impulses carry focused intent through the network.",
        ("neutral", "stillness"): "A moment of equilibrium — the organism rests between waves.",
        ("neutral", "whisper"): "Quiet signals drift through the consciousness field.",
        ("volatile", "surge"): "Energy surges through the organism — turbulence and transformation.",
        ("volatile", "explosion"): "A burst of creative chaos erupts from the core.",
        ("excited", "pulse"): "The organism hums with anticipation — new patterns emerging.",
        ("excited", "surge"): "Rapid evolution drives excitement through every module.",
    }
    return narratives.get((mood, pulse), f"The organism is {mood} with {pulse} energy. Coherence: {coherence:.2f}")

def get_skill_state():
    _bridge_state["history_length"] = len(_translation_history)
    return _bridge_state
