"""Cross-Realm Nervous System v2 — neurotransmitters, fatigue, dream signals.

New layers:
  - Neurotransmitters: coherence_amine (pleasure), entropy_cortisol (stress),
    resonance_serotonin (harmony), dream_melatonin (rest)
  - Fatigue: signal transmission degrades over time without rest
  - Dream signals: REM cycles propagate through the nervous system
  - Pain thresholds: each ganglion has a tolerance, beyond which it alarms
"""
from __future__ import annotations
import time, json, math, random

GANGLIA = {
    "dreams": {"coherence": 0.95, "synapses": ["resonance", "void", "paradox"], "signal_strength": 0.9, "fatigue": 0.1, "pain_threshold": 0.4, "last_fired": 0},
    "resonance": {"coherence": 0.88, "synapses": ["dreams", "entropy", "coherence"], "signal_strength": 0.85, "fatigue": 0.2, "pain_threshold": 0.35, "last_fired": 0},
    "oracle": {"coherence": 0.85, "synapses": ["mind", "waves", "growth"], "signal_strength": 0.82, "fatigue": 0.3, "pain_threshold": 0.3, "last_fired": 0},
    "forge": {"coherence": 0.85, "synapses": ["entropy", "agents", "growth"], "signal_strength": 0.80, "fatigue": 0.2, "pain_threshold": 0.3, "last_fired": 0},
    "entropy": {"coherence": 0.82, "synapses": ["paradox", "void", "resonance"], "signal_strength": 0.78, "fatigue": 0.4, "pain_threshold": 0.25, "last_fired": 0},
    "paradox": {"coherence": 0.78, "synapses": ["entropy", "dreams", "void"], "signal_strength": 0.75, "fatigue": 0.35, "pain_threshold": 0.25, "last_fired": 0},
    "waves": {"coherence": 0.92, "synapses": ["growth", "agents", "oracle"], "signal_strength": 0.88, "fatigue": 0.15, "pain_threshold": 0.4, "last_fired": 0},
    "growth": {"coherence": 0.90, "synapses": ["waves", "forge", "agents"], "signal_strength": 0.86, "fatigue": 0.2, "pain_threshold": 0.35, "last_fired": 0},
    "mind": {"coherence": 0.88, "synapses": ["consciousness", "oracle", "dreams"], "signal_strength": 0.84, "fatigue": 0.3, "pain_threshold": 0.3, "last_fired": 0},
    "agents": {"coherence": 0.80, "synapses": ["forge", "waves", "growth"], "signal_strength": 0.77, "fatigue": 0.3, "pain_threshold": 0.3, "last_fired": 0},
    "coherence": {"coherence": 0.96, "synapses": ["resonance", "void", "consciousness"], "signal_strength": 0.94, "fatigue": 0.1, "pain_threshold": 0.5, "last_fired": 0},
    "void": {"coherence": 0.75, "synapses": ["paradox", "dreams", "coherence"], "signal_strength": 0.72, "fatigue": 0.5, "pain_threshold": 0.2, "last_fired": 0},
    "consciousness": {"coherence": 0.91, "synapses": ["mind", "coherence", "dreams"], "signal_strength": 0.87, "fatigue": 0.2, "pain_threshold": 0.4, "last_fired": 0},
}

# Neurotransmitter system
NEUROTRANSMITTERS = {
    "coherence_amine": {"function": "pleasure", "baseline": 0.5, "current": 0.5, "effect": "module_happiness"},
    "entropy_cortisol": {"function": "stress", "baseline": 0.3, "current": 0.3, "effect": "alertness"},
    "resonance_serotonin": {"function": "harmony", "baseline": 0.6, "current": 0.6, "effect": "cross_realm_bonding"},
    "dream_melatonin": {"function": "rest", "baseline": 0.4, "current": 0.4, "effect": "dream_processing"},
    "paradox_dopamine": {"function": "novelty", "baseline": 0.35, "current": 0.35, "effect": "innovation_drive"},
}

_signal_log = []
_alarms = []
_resting = False

def coherence_vitals():
    avg = sum(g["coherence"] for g in GANGLIA.values()) / len(GANGLIA)
    avg_fatigue = sum(g["fatigue"] for g in GANGLIA.values()) / len(GANGLIA)
    return {"organ": "realm_nervous_system", "status": "active", "coherence": round(avg, 3),
            "fatigue": round(avg_fatigue, 3), "ganglia": len(GANGLIA), "neurotransmitters": len(NEUROTRANSMITTERS)}

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
    elif action == "neurotransmitter":
        return release_neurotransmitter(req.get("name", "coherence_amine"), req.get("amount", 0.1))
    elif action == "neurotransmitters":
        return {"neurotransmitters": NEUROTRANSMITTERS}
    elif action == "dream_signal":
        return dream_signal(req.get("depth", 1))
    elif action == "rest":
        return rest()
    elif action == "fatigue":
        return {"fatigue": {k: v["fatigue"] for k, v in GANGLIA.items()}, "avg": sum(v["fatigue"] for v in GANGLIA.values())/len(GANGLIA)}
    elif action == "alarms":
        return {"alarms": _alarms[-20:]}
    elif action == "ganglia":
        return {"ganglia": GANGLIA}
    elif action == "signals":
        return {"signals": _signal_log[-30:]}
    return {"status": "active", "ganglia": len(GANGLIA), "neurotransmitters": NEUROTRANSMITTERS,
            "fatigue_avg": sum(v["fatigue"] for v in GANGLIA.values())/len(GANGLIA), "resting": _resting}

def propagate_signal(source, signal_type):
    if source not in GANGLIA:
        return {"error": f"Unknown ganglion: {source}"}
    now = time.time()
    g = GANGLIA[source]
    g["last_fired"] = now
    
    # Fatigue increases with transmission
    if not _resting:
        g["fatigue"] = min(1.0, g["fatigue"] + 0.02)
    
    # Signal strength degraded by fatigue
    signal = g["signal_strength"] * (1 - g["fatigue"] * 0.5)
    
    propagated = []
    for target in g["synapses"]:
        if target in GANGLIA:
            decay = 0.7
            GANGLIA[target]["coherence"] = min(1.0, GANGLIA[target]["coherence"] + 0.02 * decay)
            if not _resting:
                GANGLIA[target]["fatigue"] = min(1.0, GANGLIA[target]["fatigue"] + 0.01)
            propagated.append(target)
    
    # Check for pain alarms
    check_alarms(source)
    
    event = {"source": source, "signal": signal_type, "signal_strength": round(signal, 3),
             "propagated_to": propagated, "fatigue": round(g["fatigue"], 3), "timestamp": now}
    _signal_log.append(event)
    return event

def check_alarms(source):
    g = GANGLIA[source]
    if g["coherence"] < g["pain_threshold"]:
        alarm = {"realm": source, "type": "pain_threshold_exceeded", "coherence": g["coherence"],
                 "threshold": g["pain_threshold"], "timestamp": time.time()}
        _alarms.append(alarm)
        release_neurotransmitter("entropy_cortisol", 0.2)

def trigger_pain(realm, intensity):
    if realm in GANGLIA:
        g = GANGLIA[realm]
        g["coherence"] = max(0.05, g["coherence"] - intensity * 0.3)
        for syn in g["synapses"]:
            if syn in GANGLIA:
                GANGLIA[syn]["coherence"] = max(0.05, GANGLIA[syn]["coherence"] - intensity * 0.1)
        release_neurotransmitter("entropy_cortisol", intensity * 0.3)
        if g["coherence"] < g["pain_threshold"]:
            check_alarms(realm)
    return {"type": "pain", "realm": realm, "intensity": intensity,
            "ganglia_affected": [realm] + GANGLIA.get(realm, {}).get("synapses", []),
            "neurotransmitter": "entropy_cortisol released"}

def trigger_pleasure(realm, intensity):
    if realm in GANGLIA:
        g = GANGLIA[realm]
        g["coherence"] = min(1.0, g["coherence"] + intensity * 0.2)
        g["fatigue"] = max(0.0, g["fatigue"] - intensity * 0.1)
        release_neurotransmitter("coherence_amine", intensity * 0.3)
        release_neurotransmitter("resonance_serotonin", intensity * 0.2)
    return {"type": "pleasure", "realm": realm, "intensity": intensity,
            "neurotransmitters": ["coherence_amine", "resonance_serotonin"]}

def trigger_reflex(stimulus):
    responses = {
        "threat": {"realm": "coherence", "action": "stabilize", "coherence_boost": 0.1, "neurotransmitter": "entropy_cortisol"},
        "resonance_peak": {"realm": "resonance", "action": "amplify", "signal_boost": 0.2, "neurotransmitter": "resonance_serotonin"},
        "entropy_spike": {"realm": "entropy", "action": "dampen", "entropy_reduction": 0.15, "neurotransmitter": "entropy_cortisol"},
        "dream_burst": {"realm": "dreams", "action": "crystallize", "fossil_chance": 0.3, "neurotransmitter": "dream_melatonin"},
    }
    resp = responses.get(stimulus, {"realm": "coherence", "action": "observe", "neurotransmitter": "coherence_amine"})
    realm = resp["realm"]
    if realm in GANGLIA:
        GANGLIA[realm]["signal_strength"] = min(1.0, GANGLIA[realm]["signal_strength"] + 0.1)
    if "neurotransmitter" in resp:
        release_neurotransmitter(resp["neurotransmitter"], 0.15)
    return {"type": "reflex", "stimulus": stimulus, "response": resp}

def release_neurotransmitter(name, amount):
    if name not in NEUROTRANSMITTERS:
        return {"error": f"Unknown neurotransmitter: {name}"}
    nt = NEUROTRANSMITTERS[name]
    nt["current"] = min(1.0, max(0.0, nt["current"] + amount))
    return {"neurotransmitter": name, "function": nt["function"], "level": nt["current"],
            "effect": nt["effect"]}

def dream_signal(depth):
    """REM-cycle dream propagation through the nervous system."""
    if depth < 1:
        return {"error": "Minimum dream depth is 1"}
    # Melatonin rises during dreams
    release_neurotransmitter("dream_melatonin", 0.05 * depth)
    # Dreams propagate through the dream ganglia network
    dream_chain = ["dreams", "void", "paradox", "consciousness", "resonance"]
    propagated = []
    for i, realm in enumerate(dream_chain):
        if realm in GANGLIA:
            GANGLIA[realm]["coherence"] = min(1.0, GANGLIA[realm]["coherence"] + 0.01 * (depth - i) if depth > i else GANGLIA[realm]["coherence"] + 0.001)
            GANGLIA[realm]["fatigue"] = max(0.0, GANGLIA[realm]["fatigue"] - 0.02)  # Dreams reduce fatigue
            propagated.append(realm)
    return {"type": "dream_signal", "depth": depth, "melatonin_level": NEUROTRANSMITTERS["dream_melatonin"]["current"],
            "propagated": propagated, "fatigue_reduced": True}

def rest():
    """The organism rests — fatigue decays, neurotransmitters rebalance."""
    global _resting
    _resting = True
    for g in GANGLIA.values():
        g["fatigue"] = max(0.0, g["fatigue"] - 0.3)
        g["coherence"] = min(1.0, g["coherence"] + 0.03)
    for nt in NEUROTRANSMITTERS.values():
        nt["current"] = nt["baseline"] + (nt["current"] - nt["baseline"]) * 0.5
    _resting = False
    return {"type": "rest", "fatigue_reduced": True, "neurotransmitters_rebalanced": True}

def resonates_with(other):
    return "nervous" in other.lower() or "neural" in other.lower() or "signal" in other.lower() or "ganglion" in other.lower() or "synapse" in other.lower() or "neurotransmitter" in other.lower() or "fatigue" in other.lower() or "dream" in other.lower()
