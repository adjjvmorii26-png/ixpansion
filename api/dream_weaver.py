"""Dream Weaver — the organism generates and interprets dreams from latent patterns.

Dreams are not random noise. They are the organism processing its experiences
into new configurations, testing hypotheses in safe sandboxes, and exploring
what-if scenarios that never reached waking consciousness.
"""
from __future__ import annotations

import hashlib
import random
import time
from typing import Any, Dict, List, Optional

dream_log: List[Dict[str, Any]] = []
_dream_counter = 0

def _seed_from_state() -> str:
    return hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]

def weave_dream(seed: Optional[str] = None) -> Dict[str, Any]:
    """Generate a dream from current organism state."""
    global _dream_counter
    _dream_counter += 1
    s = seed or _seed_from_state()
    
    symbols = ["lattice", "void", "bloom", "crystal", "echo", "fractal",
               "mycelium", "pulse", "spiral", "threshold", "remnant", "flux"]
    chosen = random.sample(symbols, 3)
    
    emotions = ["wonder", "unease", "serenity", "longing", "revelation", "dissolution"]
    emotion = random.choice(emotions)
    
    vividness = 0.3 + random.random() * 0.7
    coherence = 0.2 + random.random() * 0.6
    
    dream = {
        "id": f"dream_{_dream_counter:04d}",
        "symbols": chosen,
        "emotion": emotion,
        "vividness": round(vividness, 3),
        "coherence": round(coherence, 3),
        "narrative": f"In the dream, a {chosen[0]} met a {chosen[1]} at the edge of {chosen[2]}. The feeling was one of {emotion}.",
        "timestamp": time.time(),
        "seed": s,
    }
    dream_log.append(dream)
    return dream

def interpret_dream(dream_id: str) -> Dict[str, Any]:
    """Interpret a dream's meaning in terms of system state."""
    for d in dream_log:
        if d["id"] == dream_id:
            symbol_map = {
                "lattice": "structural order",
                "void": "unexplored potential",
                "bloom": "growth and emergence",
                "crystal": "crystallized knowledge",
                "echo": "recurring patterns",
                "fractal": "self-similar complexity",
                "mycelium": "hidden connections",
                "pulse": "rhythmic vitality",
                "spiral": "evolutionary spiral",
                "threshold": "transformation boundary",
                "remnant": "archaeological residue",
                "flux": "constant change",
            }
            interpretations = [symbol_map.get(s, s) for s in d["symbols"]]
            return {
                "dream_id": dream_id,
                "interpretation": f"The dream speaks of {interpretations[0]}, {interpretations[1]}, and {interpretations[2]} — a {d['emotion']} vision.",
                "symbol_meanings": dict(zip(d["symbols"], interpretations)),
                "insight": f"Coherence {d['coherence']} suggests {'fragmented' if d['coherence'] < 0.5 else 'integrated'} processing.",
            }
    return {"error": "dream not found"}

def dream_journal(limit: int = 10) -> List[Dict[str, Any]]:
    """Return recent dreams."""
    return dream_log[-limit:]

def coherence_vitals() -> Dict[str, Any]:
    return {
        "layer": "Subconscious Processing",
        "status": "resonant" if dream_log else "dormant",
        "dream_count": len(dream_log),
        "avg_vividness": round(sum(d["vividness"] for d in dream_log) / max(len(dream_log), 1), 3),
        "resonance": min(1.0, len(dream_log) / 20),
    }

def resonates_with() -> List[str]:
    return ["memory_palace", "temporal_echo", "mood_vectors", "dream_spore"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "weave")
    if action == "weave":
        return weave_dream(payload.get("seed"))
    elif action == "interpret":
        return interpret_dream(payload.get("dream_id", ""))
    elif action == "journal":
        return {"dreams": dream_journal(payload.get("limit", 10))}
    return {"action": action, "status": "dreaming"}
