"""
visual_metaphor_engine — Converts abstract concepts into visual metaphors.
Translates system states, data patterns, and emotions into imagery.
"""
import hashlib
import time
import random
from typing import Dict, List

_skill_active = False
_metaphors = []

METAPHOR_MAP = {
    "high_coherence": ["a crystal cathedral refracting light", "a perfectly tuned orchestra", "a galaxy in harmonic orbit"],
    "low_coherence": ["scattered puzzle pieces in wind", "a broken mirror reflecting different worlds", "static between radio stations"],
    "high_entropy": ["a kaleidoscope mid-spin", "fireworks dissolving into smoke", "a crowd of unrelated conversations"],
    "low_entropy": ["a still frozen lake", "a single perfect snowflake", "the pause between heartbeats"],
    "rising_mood": ["dawn breaking over mountains", "a flower opening to sunlight", "a kite catching upward wind"],
    "falling_mood": ["autumn leaves descending", "tides pulling back from shore", "a candle flickering low"],
    "phase_transition": ["butterfly emerging from chrysalis", "ice cracking on a spring lake", "a dam about to break"],
    "emergence": ["mushroom ring appearing overnight", "aurora borealis forming patterns", "a murmuration of starlings"]
}

def activate_skill(params=None):
    global _skill_active
    _skill_active = True
    return {"status": "activated", "skill": "visual_metaphor_engine", "activated_at": time.time()}

def visualize(state: str, coherence: float = 0.5, entropy: float = 0.5) -> Dict:
    key = state
    if coherence > 0.7: key = "high_coherence"
    elif coherence < 0.3: key = "low_coherence"
    elif entropy > 0.7: key = "high_entropy"
    elif entropy < 0.3: key = "low_entropy"
    
    images = METAPHOR_MAP.get(key, METAPHOR_MAP["high_coherence"])
    metaphor = random.choice(images)
    
    result = {"state": state, "metaphor": metaphor, "key": key,
              "palette": _state_to_palette(coherence, entropy), "timestamp": time.time()}
    _metaphors.append(result)
    if len(_metaphors) > 50: _metaphors.pop(0)
    return result

def _state_to_palette(c: float, e: float) -> List[str]:
    if c > 0.7: return ["#7c7cf8", "#a78bfa", "#c4b5fd"]
    if e > 0.7: return ["#fb7185", "#f43f5e", "#e11d48"]
    if c > 0.5: return ["#2dd4bf", "#5eead4", "#99f6e4"]
    return ["#fbbf24", "#f59e0b", "#d97706"]

def get_metaphors(limit: int = 10) -> List[Dict]:
    return _metaphors[-limit:]

def get_skill_state():
    return {"name": "visual_metaphor_engine", "active": _skill_active,
            "capabilities": ["visualize"], "metaphors": len(_metaphors)}
