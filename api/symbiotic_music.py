"""Symbiotic Music — the organism composes ambient soundscapes from its state.

Coherence level becomes tempo. Active modules become instruments.
Recent events become melody. The organism's inner life gets a living soundtrack
that evolves in real-time as the system changes.
"""
from __future__ import annotations

import hashlib
import math
import time
from typing import Any, Dict, List, Optional

compositions: List[Dict[str, Any]] = []

# Musical scale in MIDI-like note names
_SCALE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def _hash_to_note(h: str) -> str:
    """Convert a hex char to a musical note."""
    idx = int(h, 16) % len(_SCALE)
    octave = 3 + (idx // 4)
    return f"{_SCALE[idx]}{octave}"

def _state_to_tempo(coherence: float) -> int:
    """Coherence maps to tempo: high coherence = calm, low = frantic."""
    return int(60 + (1.0 - coherence) * 100)

def compose_from_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a musical composition from organism state."""
    coherence = state.get("coherence", 0.8)
    module_count = state.get("modules", 0)
    wave = state.get("wave", 0)
    energy = state.get("energy", 0.5)
    
    # Tempo from coherence
    tempo = _state_to_tempo(coherence)
    
    # Key from wave number
    key = _SCALE[wave % len(_SCALE)]
    
    # Generate melody from module count hash
    h = hashlib.md5(str(module_count).encode()).hexdigest()
    melody = [_hash_to_note(h[i]) for i in range(min(16, len(h)))]
    
    # Instruments based on energy level
    instruments = []
    if energy > 0.7:
        instruments = ["synth_pad", "bells", "bass", "drums"]
    elif energy > 0.4:
        instruments = ["synth_pad", "piano", "bass"]
    else:
        instruments = ["piano", "strings"]
    
    composition = {
        "tempo": tempo,
        "key": f"{key} major",
        "time_signature": "4/4",
        "melody": melody,
        "instruments": instruments,
        "duration_bars": 16,
        "mood": "contemplative" if coherence > 0.8 else "urgent" if coherence < 0.5 else "flowing",
        "coherence": round(coherence, 3),
        "generated_at": time.time(),
    }
    compositions.append(composition)
    return composition

def music_history() -> List[Dict[str, Any]]:
    """Return recent compositions."""
    return compositions[-5:]

def coherence_vitals() -> Dict[str, Any]:
    return {
        "layer": "Aesthetic Expression",
        "status": "resonant" if compositions else "dormant",
        "compositions": len(compositions),
        "resonance": min(1.0, len(compositions) / 10),
    }

def resonates_with() -> List[str]:
    return ["choral_engine", "sound_cauldron", "codecalligraphy", "mood_vectors"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "compose")
    if action == "compose":
        state = payload.get("state", {"coherence": 0.8, "modules": 252, "wave": 204, "energy": 0.6})
        return compose_from_state(state)
    elif action == "history":
        return {"history": music_history()}
    return {"action": action, "compositions": len(compositions)}
