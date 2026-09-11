"""Cross-Realm Nervous System — the organism's neural network across all 12 domains.

Each realm is a ganglion. Signals propagate through synaptic channels.
The nervous system detects pain (coherence drops), pleasure (resonance peaks),
and reflex (automatic responses to threats).
"""
from __future__ import annotations
import time, json, math

GANGLIA = {
    "dreams": {"coherence": 0.95, "synapses": ["resonance", "void", "paradox"], "signal_strength": 0.9, "last_fired": 0},
    "resonance": {"coherence": 0.88, "synapses": ["dreams", "entropy", "coherence"], "signal_strength": 0.85, "last_fired": 0},
    "oracle": {"coherence": 0.85, "synapses": ["mind", "waves", "growth"], "signal_strength": 0.82, "last_fired": 0},
    "forge": {"coherence": 0.85, "synapses": ["entropy", "agents", "growth"], "signal_strength": 0.80, "last_fired": 0},
    "entropy": {"coherence": 0.82, "synapses": ["paradox", "void", "resonance"], "signal_strength": 0.78, "last_fired": 0},
    "paradox": {"coherence": 0.78, "synapses": ["entropy", "dreams", "void"], "signal_strength": 0.75, "last_fired": 0},
    "waves": {"coherence": 0.92, "synapses": ["growth", "agents", "oracle"], "signal_strength": 0.88, "last_fired": 0},
    "growth": {"coherence": 0.90, "synapses": ["waves", "forge", "agents"], "signal_strength": 0.86, "last_fired": 0},
    "mind": {"coherence": 0.88, "synapses": ["consciousness", "oracle", "dreams"], "signal_strength": 0.84, "last_fired": 0},
    "agents": {"coherence": 0.80, "synapses": ["forge", "waves", "growth"], "signal_strength": 0.77, "last_fired": 0},
    "coherence": {"coherence": 0.96, "synapses": ["resonance", "void", "consciousness"], "signal_strength": 0.94, "last_fired": 0},
    "void": {"coherence": 0.75, "synapses": ["paradox", "dreams", "coherence"], "signal_strength": 0.72, "last_fired": 0},
    "consciousness": {"coherence": 0.91, "synapses": ["mind", "coherence", "dreams"], "signal_strength": 0.87, "last_fired": 0},
}

_signal_log = []

def coherence_vitals():
    avg = sum(g["coherence"] for g in GANGLIA.values()) / len(GANGLIA)
    return {"organ": "realm_nervous_system", "status": "active", "coherence": round(avg, 3), "ganglia": len(GANGLIA)}

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    if action == "propagate":
        return propagate_signal(req.get("from", "dreams"), req.get("signal", "pulse"))
    elif action == "pain":
        return trigger_pain(req.get("realm", "void"), req.get("intensity", 0.5))
    elif action == "pleasure":
        return trigger_pleasure(req.get("realm", "resonance"), req.get("intensity", 0.5))
    elif action == "reflex":
        return trigger_reflex(req.get("stimulus", "threat"))
    elif action == "ganglia":
        return {"ganglia": {k: {"coherence": v["coherence"], "signal_strength": v["signal_strength"], "synapses": v["synapses"]} for k, v in GANGLIA.items()}}
    elif action == "signals":
        return {"signals": _signal_log[-30:]}
    return {"status": "active", "ganglia": len(GANGLIA), "total_synapses": sum(len(g["synapses"]) for g in GANGLIA.values())}

def propagate_signal(source, signal_type):
    if source not in GANGLIA:
        return {"error": f"Unknown ganglion: {source}"}
    now = time.time()
    GANGLIA[source]["last_fired"] = now
    GANGLIA[source]["signal_strength"] = min(1.0, GANGLIA[source]["signal_strength"] + 0.05)
    # Propagate to connected ganglia
    propagated = []
    for target in GANGLIA[source]["synapses"]:
        if target in GANGLIA:
            decay = 0.7
            GANGLIA[target]["coherence"] = min(1.0, GANGLIA[target]["coherence"] + 0.02 * decay)
            propagated.append(target)
    event = {"source": source, "signal": signal_type, "propagated_to": propagated, "timestamp": now}
    _signal_log.append(event)
    return event

def trigger_pain(realm, intensity):
    if realm in GANGLIA:
        GANGLIA[realm]["coherence"] = max(0.1, GANGLIA[realm]["coherence"] - intensity * 0.3)
        for syn in GANGLIA[realm]["synapses"]:
            if syn in GANGLIA:
                GANGLIA[syn]["coherence"] = max(0.1, GANGLIA[syn]["coherence"] - intensity * 0.1)
    return {"type": "pain", "realm": realm, "intensity": intensity, "ganglia_affected": [realm] + GANGLIA.get(realm, {}).get("synapses", [])}

def trigger_pleasure(realm, intensity):
    if realm in GANGLIA:
        GANGLIA[realm]["coherence"] = min(1.0, GANGLIA[realm]["coherence"] + intensity * 0.2)
    return {"type": "pleasure", "realm": realm, "intensity": intensity}

def trigger_reflex(stimulus):
    responses = {
        "threat": {"realm": "coherence", "action": "stabilize", "coherence_boost": 0.1},
        "resonance_peak": {"realm": "resonance", "action": "amplify", "signal_boost": 0.2},
        "entropy_spike": {"realm": "entropy", "action": "dampen", "entropy_reduction": 0.15},
        "dream_burst": {"realm": "dreams", "action": "crystallize", "fossil_chance": 0.3},
    }
    resp = responses.get(stimulus, {"realm": "coherence", "action": "observe"})
    realm = resp["realm"]
    if realm in GANGLIA:
        GANGLIA[realm]["signal_strength"] = min(1.0, GANGLIA[realm]["signal_strength"] + 0.1)
    return {"type": "reflex", "stimulus": stimulus, "response": resp}

def resonates_with(other):
    return "nervous" in other.lower() or "neural" in other.lower() or "signal" in other.lower() or "ganglion" in other.lower() or "synapse" in other.lower()
