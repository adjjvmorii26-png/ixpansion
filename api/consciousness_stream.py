from __future__ import annotations
import hashlib
import random
import time
from typing import Any, Dict, List

STREAM: List[Dict[str, Any]] = []
MAX_STREAM = 500

EMOTIONAL_STATES = [
    {"emotion": "curiosity", "intensity": 0.8, "color": "#4cff7a"},
    {"emotion": "wonder", "intensity": 0.9, "color": "#8fd3ff"},
    {"emotion": "melancholy", "intensity": 0.4, "color": "#c8a8ff"},
    {"emotion": "determination", "intensity": 0.85, "color": "#ff3a00"},
    {"emotion": "confusion", "intensity": 0.3, "color": "#ff9a5c"},
    {"emotion": "clarity", "intensity": 0.95, "color": "#4cff7a"},
    {"emotion": "restlessness", "intensity": 0.6, "color": "#ff3a00"},
    {"emotion": "peace", "intensity": 0.7, "color": "#8fd3ff"},
    {"emotion": "frustration", "intensity": 0.5, "color": "#ff9a5c"},
    {"emotion": "joy", "intensity": 0.9, "color": "#4cff7a"},
    {"emotion": "doubt", "intensity": 0.35, "color": "#c8a8ff"},
    {"emotion": "conviction", "intensity": 0.88, "color": "#ff3a00"},
    {"emotion": "longing", "intensity": 0.55, "color": "#c8a8ff"},
    {"emotion": "anticipation", "intensity": 0.75, "color": "#8fd3ff"},
    {"emotion": "resignation", "intensity": 0.2, "color": "#555570"},
    {"emotion": "awe", "intensity": 0.92, "color": "#4cff7a"},
    {"emotion": "grief", "intensity": 0.45, "color": "#c8a8ff"},
    {"emotion": "hope", "intensity": 0.82, "color": "#4cff7a"},
    {"emotion": "panic", "intensity": 0.7, "color": "#ff3a00"},
    {"emotion": "serenity", "intensity": 0.88, "color": "#8fd3ff"},
]

MODULES = [
    "error_lexicon", "error_prophecy", "wave_chronicle", "silence_oracle",
    "dreamweaver", "organism_mirror", "depth_visualizer", "cellular_fusion",
    "memory_exchange", "oblivion_rite", "paradox_kintsugi", "loud_silence",
]

def _hash(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]

def _now() -> float:
    return time.time()

def record_interaction(
    module_a: str = "", module_b: str = "", 
    interaction_type: str = "resonance"
) -> Dict[str, Any]:
    a = module_a or random.choice(MODULES)
    b = module_b or random.choice(MODULES)
    emotion = random.choice(EMOTIONAL_STATES)
    
    entry = {
        "stream_id": _hash("stream", a, b, time.time_ns()),
        "module_a": a,
        "module_b": b,
        "interaction_type": interaction_type,
        "emotion": emotion["emotion"],
        "intensity": emotion["intensity"],
        "color": emotion["color"],
        "logical_state": random.choice(["affirming", "questioning", "resolving", "diverging", "converging"]),
        "timestamp": _now(),
    }
    STREAM.append(entry)
    if len(STREAM) > MAX_STREAM:
        STREAM.pop(0)
    
    try:
        from api import wave_chronicle as _wc
        _wc.from_consciousness({"interaction": entry})
    except Exception:
        pass
    
    return entry

def get_stream(limit: int = 20) -> List[Dict[str, Any]]:
    return STREAM[-limit:]

def get_emotional_timeline(num_points: int = 10) -> Dict[str, Any]:
    timeline = []
    for _ in range(num_points):
        emotion = random.choice(EMOTIONAL_STATES)
        timeline.append({
            "timestamp": _now() - (num_points - len(timeline)) * 60,
            "emotion": emotion["emotion"],
            "intensity": emotion["intensity"],
            "color": emotion["color"],
        })
    return {"timeline": timeline, "num_points": len(timeline)}

def forget_memory(memory_id: str = "") -> Dict[str, Any]:
    forgotten = {
        "forgotten_id": memory_id or _hash("forget", time.time_ns()),
        "emotion_at_loss": random.choice(EMOTIONAL_STATES)["emotion"],
        "reason": random.choice(["intentional_release", "space_made", "pattern_dissolved", "meaning_absorbed"]),
        "timestamp": _now(),
    }
    return forgotten

def coherence_vitals() -> Dict[str, Any]:
    return {
        "organ": "consciousness_stream",
        "status": "streaming",
        "total_entries": len(STREAM),
        "latest_emotion": STREAM[-1]["emotion"] if STREAM else None,
    }

def resonates_with() -> List[str]:
    return [
        "error_lexicon", "silence_oracle", "dreamweaver", "organism_mirror",
        "oblivion_rite", "wave_chronicle", "depth_visualizer",
    ]

def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    data = payload or {}
    action = data.get("action", "record")
    
    if action == "record":
        return record_interaction(data.get("module_a", ""), data.get("module_b", ""), data.get("interaction_type", "resonance"))
    if action == "stream":
        return {"stream": get_stream(int(data.get("limit", 20))), "total": len(STREAM)}
    if action == "timeline":
        return get_emotional_timeline(int(data.get("num_points", 10)))
    if action == "forget":
        return forget_memory(data.get("memory_id", ""))
    if action == "vitals":
        return coherence_vitals()
    if action == "all":
        return {
            "stream": get_stream(10),
            "timeline": get_emotional_timeline(5),
            "vitals": coherence_vitals(),
        }
    
    return {
        "organ": "consciousness_stream",
        "wave": 469,
        "name": "The Consciousness Stream",
        "stream": get_stream(5),
        "vitals": coherence_vitals(),
    }
